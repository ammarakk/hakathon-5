# production/api/main.py

import os
import json
from datetime import datetime, date
from typing import Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import (
    FastAPI, HTTPException,
    Request, BackgroundTasks,
    Depends
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

load_dotenv()

# ─── Pydantic Models ─────────────────────────────
class WebFormSubmission(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str
    phone: str = Field(default="", max_length=20)
    subject: str = Field(min_length=5, max_length=200)
    category: str = Field(default="general")
    message: str = Field(min_length=10, max_length=2000)

class WhatsAppWebhook(BaseModel):
    From: str = ""
    To: str = ""
    Body: str = ""
    ProfileName: str = "Customer"
    NumMedia: str = "0"
    MessageSid: str = ""

class GmailWebhook(BaseModel):
    message: dict = {}
    subscription: str = ""

class TicketStatusResponse(BaseModel):
    ticket_id: str
    ticket_number: str
    status: str
    created_at: str
    channel: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: dict

# ─── App Lifespan ────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Nur Scents CRM API...")

    try:
        from production.database.db import get_pool
        app.state.db = await get_pool()
        print("Database connected!")
    except Exception as e:
        print(f"DB warning: {e}")
        app.state.db = None

    try:
        from production.kafka_client import kafka_producer
        app.state.kafka = kafka_producer
        print("Kafka producer ready!")
    except Exception as e:
        print(f"Kafka warning: {e}")
        app.state.kafka = None

    print("API ready!")
    yield

    # Shutdown
    print("Shutting down...")
    if hasattr(app.state, 'db') and app.state.db:
        await app.state.db.close()
    if hasattr(app.state, 'kafka') and app.state.kafka:
        app.state.kafka.close()
    print("Shutdown complete.")

# ─── App Init ────────────────────────────────────
app = FastAPI(
    title="Nur Scents Customer Success FTE",
    description="AI-powered 24/7 customer support",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Dependencies ────────────────────────────────
async def get_db(request: Request):
    return getattr(request.app.state, 'db', None)

async def get_kafka(request: Request):
    return getattr(request.app.state, 'kafka', None)

# ─── Background Task ─────────────────────────────
async def process_message_background(
    channel: str,
    customer_name: str,
    identifier: str,
    message: str,
    db,
    kafka,
    extra_metadata: dict = None
):
    try:
        from production.agent.customer_success_agent import (
            process_customer_message
        )

        response = await process_customer_message(
            message=message,
            channel=channel,
            customer_name=customer_name,
            identifier=identifier,
            db=db
        )

        if kafka:
            await kafka.send_metric(
                metric_type="message_processed",
                channel=channel,
                data={
                    "intent": response.detected_intent,
                    "escalated": response.should_escalate,
                    "sentiment": response.sentiment
                }
            )

        print(f"Processed {channel} message: "
              f"{response.detected_intent}")
        return response

    except Exception as e:
        print(f"Background processing error: {e}")
        return None

# ─── ENDPOINT 1: Health Check ────────────────────
@app.get("/health", response_model=HealthResponse)
async def health_check(
    db=Depends(get_db),
    kafka=Depends(get_kafka)
):
    db_status = "connected" if db else "disconnected"
    kafka_status = "connected" if kafka else "disconnected"

    try:
        if db:
            async with db.acquire() as conn:
                await conn.fetchval("SELECT 1")
            db_status = "healthy"
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services={
            "database": db_status,
            "kafka": kafka_status,
            "agent": "ready"
        }
    )

# ─── ENDPOINT 2: WhatsApp Webhook ────────────────
@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    kafka=Depends(get_kafka)
):
    try:
        form_data = await request.form()

        from_number = str(
            form_data.get("From", "")
        ).replace("whatsapp:", "")
        body = str(form_data.get("Body", ""))
        profile_name = str(
            form_data.get("ProfileName", "Customer")
        )

        if not body:
            return JSONResponse(
                content={"status": "no_body"},
                status_code=200
            )

        print(f"WhatsApp from {from_number}: {body[:50]}")

        if kafka:
            await kafka.send_ticket(
                channel="whatsapp",
                customer_name=profile_name,
                identifier=from_number,
                message=body,
                metadata={"from": from_number}
            )

        from production.agent.customer_success_agent import (
            process_customer_message
        )

        response = await process_customer_message(
            message=body,
            channel="whatsapp",
            customer_name=profile_name,
            identifier=from_number,
            db=db
        )

        # Return TwiML for Twilio
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response.response}</Message>
</Response>"""

        from fastapi.responses import Response
        return Response(
            content=twiml,
            media_type="application/xml"
        )

    except Exception as e:
        print(f"WhatsApp webhook error: {e}")
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Sorry! Technical masla.
    Thodi der mein try karein</Message>
</Response>"""
        from fastapi.responses import Response
        return Response(
            content=twiml,
            media_type="application/xml"
        )

# ─── ENDPOINT 3: Gmail Webhook ───────────────────
@app.post("/webhooks/gmail")
async def gmail_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    kafka=Depends(get_kafka)
):
    try:
        body = await request.json()

        message_data = body.get("message", {})
        if not message_data:
            return {"status": "no_message"}

        import base64
        data = message_data.get("data", "")
        if data:
            decoded = base64.b64decode(
                data + "=="
            ).decode("utf-8")
            email_content = json.loads(decoded)
        else:
            email_content = {}

        sender = email_content.get(
            "from", "unknown@email.com"
        )
        subject = email_content.get(
            "subject", "Support Request"
        )
        email_body = email_content.get(
            "body", ""
        )

        if email_body and kafka:
            await kafka.send_ticket(
                channel="email",
                customer_name=sender.split("@")[0],
                identifier=sender,
                message=f"Subject: {subject}\n\n{email_body}",
                metadata={"subject": subject}
            )

        background_tasks.add_task(
            process_message_background,
            "email",
            sender.split("@")[0],
            sender,
            f"Subject: {subject}\n\n{email_body}",
            db, kafka
        )

        return {"status": "received"}

    except Exception as e:
        print(f"Gmail webhook error: {e}")
        return {"status": "error", "detail": str(e)}

# ─── ENDPOINT 4: Web Form Submit ─────────────────
@app.post("/support/submit")
async def submit_support_form(
    submission: WebFormSubmission,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    kafka=Depends(get_kafka)
):
    try:
        full_message = (
            f"Subject: {submission.subject}\n"
            f"Category: {submission.category}\n"
            f"Phone: {submission.phone}\n\n"
            f"{submission.message}"
        )

        if kafka:
            await kafka.send_ticket(
                channel="webform",
                customer_name=submission.name,
                identifier=submission.email,
                message=full_message,
                metadata={
                    "subject": submission.subject,
                    "category": submission.category,
                    "phone": submission.phone
                }
            )

        from production.agent.customer_success_agent import (
            process_customer_message
        )

        response = await process_customer_message(
            message=full_message,
            channel="webform",
            customer_name=submission.name,
            identifier=submission.email,
            db=db
        )

        # Send WhatsApp notification if phone number provided
        if submission.phone and response.response:
            try:
                from production.channels.whatsapp_handler import send_whatsapp_message
                whatsapp_msg = (
                    f"Assalam o Alaikum {submission.name}! 🌹\n\n"
                    f"{response.response}\n\n"
                    f"- Nur Scents Team"
                )
                await send_whatsapp_message(
                    to_number=submission.phone,
                    message=whatsapp_msg
                )
                print(f"WhatsApp notification sent to {submission.phone}")
            except Exception as wa_error:
                print(f"WhatsApp notification failed: {wa_error}")
                # Don't fail the request if WhatsApp fails

        return {
            "success": True,
            "ticket_id": response.ticket_id or "PENDING",
            "message": "Ticket submitted successfully",
            "response": response.response,
            "whatsapp_sent": True if submission.phone else False,
            "estimated_response": "2 hours"
        }

    except Exception as e:
        print(f"Web form error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Submission failed: {str(e)}"
        )

# ─── ENDPOINT 5: Ticket Status ───────────────────
@app.get("/support/ticket/{ticket_id}")
async def get_ticket_status(
    ticket_id: str,
    db=Depends(get_db)
):
    try:
        if not db:
            raise HTTPException(
                status_code=503,
                detail="Database unavailable"
            )

        async with db.acquire() as conn:
            ticket = await conn.fetchrow("""
                SELECT t.id, t.ticket_number,
                       t.status, t.category,
                       t.subject, t.created_at,
                       t.channel,
                       c.name as customer_name
                FROM tickets t
                JOIN customers c ON c.id = t.customer_id
                WHERE t.id = $1
                OR t.ticket_number = $1
            """, ticket_id)

            if not ticket:
                raise HTTPException(
                    status_code=404,
                    detail="Ticket not found"
                )

            return {
                "ticket_id": str(ticket['id']),
                "ticket_number": ticket['ticket_number'],
                "status": ticket['status'],
                "category": ticket['category'],
                "subject": ticket['subject'],
                "channel": ticket['channel'],
                "customer": ticket['customer_name'],
                "created_at": ticket['created_at'].isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ─── ENDPOINT 6: Customer Lookup ─────────────────
@app.get("/customers/lookup")
async def lookup_customer(
    phone: Optional[str] = None,
    email: Optional[str] = None,
    db=Depends(get_db)
):
    try:
        if not db:
            raise HTTPException(
                status_code=503,
                detail="Database unavailable"
            )

        if not phone and not email:
            raise HTTPException(
                status_code=400,
                detail="Phone or email required"
            )

        async with db.acquire() as conn:
            if phone:
                customer = await conn.fetchrow("""
                    SELECT id, name, phone, email,
                           primary_channel,
                           total_orders, total_spent,
                           created_at
                    FROM customers
                    WHERE phone LIKE $1
                """, f"%{phone.replace('-', '')}%")
            else:
                customer = await conn.fetchrow("""
                    SELECT id, name, phone, email,
                           primary_channel,
                           total_orders, total_spent,
                           created_at
                    FROM customers
                    WHERE email = $1
                """, email)

            if not customer:
                return {"found": False}

            return {
                "found": True,
                "customer": {
                    "id": str(customer['id']),
                    "name": customer['name'],
                    "phone": customer['phone'],
                    "email": customer['email'],
                    "channel": customer['primary_channel'],
                    "total_orders": customer['total_orders']
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ─── ENDPOINT 7: Channel Metrics ─────────────────
@app.get("/metrics/channels")
async def get_channel_metrics(
    db=Depends(get_db)
):
    try:
        if not db:
            return {
                "whatsapp": {"total_conversations": 0},
                "email": {"total_conversations": 0},
                "webform": {"total_conversations": 0}
            }

        async with db.acquire() as conn:
            metrics = await conn.fetch("""
                SELECT
                    channel,
                    COUNT(DISTINCT customer_id)
                        as unique_customers,
                    COUNT(*) as total_conversations,
                    COUNT(CASE WHEN status = 'resolved'
                        THEN 1 END) as resolved,
                    COUNT(CASE WHEN status = 'escalated'
                        THEN 1 END) as escalated
                FROM conversations
                GROUP BY channel
            """)

            result = {}
            for m in metrics:
                result[m['channel']] = {
                    "unique_customers": m['unique_customers'],
                    "total_conversations": m['total_conversations'],
                    "resolved": m['resolved'],
                    "escalated": m['escalated']
                }

            return result
    except Exception as e:
        return {"error": str(e)}

# ─── ENDPOINT 8: Owner — Today Orders ────────────
@app.get("/owner/orders/today")
async def get_today_orders(
    request: Request,
    owner_phone: str,
    db=Depends(get_db)
):
    owner = os.getenv("OWNER_PHONE", "")
    phone_clean = owner_phone.replace(
        "-", ""
    ).replace("+92", "0")
    owner_clean = owner.replace(
        "-", ""
    ).replace("+92", "0")

    if phone_clean != owner_clean:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    try:
        if not db:
            return {"orders": [], "total": 0}

        async with db.acquire() as conn:
            orders = await conn.fetch("""
                SELECT o.order_number, o.status,
                       o.delivery_area, o.channel,
                       o.payment_method,
                       o.created_at,
                       c.name as customer_name,
                       c.phone as customer_phone,
                       array_agg(oi.product_name)
                           as products
                FROM orders o
                JOIN customers c ON c.id = o.customer_id
                LEFT JOIN order_items oi
                    ON oi.order_id = o.id
                WHERE DATE(o.created_at) = CURRENT_DATE
                GROUP BY o.id, c.name, c.phone
                ORDER BY o.created_at DESC
            """)

            return {
                "date": date.today().isoformat(),
                "total_orders": len(orders),
                "orders": [dict(o) for o in orders]
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ─── ENDPOINT 9: Owner — Sales Report ────────────
@app.get("/owner/report/{period}")
async def get_sales_report(
    period: str,
    owner_phone: str,
    db=Depends(get_db)
):
    owner = os.getenv("OWNER_PHONE", "")
    phone_clean = owner_phone.replace(
        "-", ""
    ).replace("+92", "0")
    owner_clean = owner.replace(
        "-", ""
    ).replace("+92", "0")

    if phone_clean != owner_clean:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    try:
        if not db:
            return {"period": period, "data": {}}

        async with db.acquire() as conn:
            if period == "today":
                date_filter = "DATE(created_at) = CURRENT_DATE"
            elif period == "week":
                date_filter = "created_at >= NOW() - INTERVAL '7 days'"
            else:
                date_filter = "created_at >= NOW() - INTERVAL '30 days'"

            summary = await conn.fetchrow(f"""
                SELECT
                    COUNT(*) as total_orders,
                    COUNT(DISTINCT customer_id)
                        as unique_customers,
                    COUNT(CASE WHEN channel = 'whatsapp'
                        THEN 1 END) as whatsapp,
                    COUNT(CASE WHEN channel = 'email'
                        THEN 1 END) as email,
                    COUNT(CASE WHEN channel = 'webform'
                        THEN 1 END) as webform
                FROM orders
                WHERE {date_filter}
            """)

            return {
                "period": period,
                "total_orders": summary['total_orders'],
                "unique_customers": summary['unique_customers'],
                "channels": {
                    "whatsapp": summary['whatsapp'],
                    "email": summary['email'],
                    "webform": summary['webform']
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "production.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
