# Enable Google Cloud Billing for Nur Scents CRM

## Step 1: Go to Google Cloud Console
https://console.cloud.google.com/billing

## Step 2: Create Billing Account
1. Click "Create account"
2. Fill in your details:
   - Country: Pakistan
   - Name: [Your Name]
   - Address: [Your Address]
   - Payment Method: Credit Card

## Step 3: Set Budget Alerts (IMPORTANT!)
1. After creating billing account, click "Set budget"
2. Set daily budget: $5-10 USD (recommended)
3. This prevents unexpected charges
4. You'll get alerts at 50%, 75%, 90% and 100%

## Step 4: Link Project to Billing Account
1. Your project should automatically link
2. Or go to: https://console.cloud.google.com/billing/projects
3. Select your project and link billing account

## Step 5: Verify Billing is Active
1. Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
2. You should see "API enabled"
3. Quota limits should be removed

## Step 6: Test Your CRM
Run: python test_crm_direct.py

Expected output:
- No quota errors
- AI responds in Urdu/English
- Product recommendations
- Order creation

## Costs (Estimated)
- Free tier: 15 requests/day (you're over this)
- Paid tier: $0.002 per request
- 100 customers/day = $0.20 USD
- 1000 customers/day = $2.00 USD

## Safety
- Budget alerts prevent overspending
- You can set maximum spending limits
- Billing can be paused anytime
- Daily spending reports available
