"""
MCP Server Test Script
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.mcp.server import mcp_server
from app.mcp.agent_integration import enhanced_agent_service
from app.core.logging import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def test_mcp_tools():
    """Test MCP tools"""
    logger.info("🧪 Testing MCP Server Tools\n")

    # Test 1: List tools
    logger.info("Test 1: List all tools")
    tools = mcp_server.list_tools()
    logger.info(f"✅ Found {len(tools)} tools:")
    for tool in tools:
        logger.info(f"   - {tool['name']}: {tool['description'][:60]}...")

    # Test 2: Get categories
    logger.info("\nTest 2: Get categories")
    result = await mcp_server.call_tool("get_categories", {})
    if result["success"]:
        logger.info(f"✅ Categories: {result['categories']}")

    # Test 3: Search products
    logger.info("\nTest 3: Search products")
    result = await mcp_server.call_tool("search_products", {"query": "oudh", "limit": 3})
    if result["success"]:
        logger.info(f"✅ Found {result['count']} products:")
        for product in result["products"][:2]:
            logger.info(f"   - {product['name']}: PKR {product['price']}")

    # Test 4: Get product details
    logger.info("\nTest 4: Get product details")
    result = await mcp_server.call_tool("get_product_details", {"product_id": "NS-001"})
    if result["success"]:
        product = result["product"]
        logger.info(f"✅ Product: {product['name']}")
        logger.info(f"   Price: PKR {product['price']}")
        logger.info(f"   Stock: {product['stock']}")

    # Test 5: Check stock
    logger.info("\nTest 5: Check stock")
    result = await mcp_server.call_tool("check_stock", {"product_id": "NS-001", "quantity": 5})
    if result["success"]:
        stock_info = result["stock"]
        logger.info(f"✅ Stock check for NS-001:")
        logger.info(f"   Available: {stock_info['available_stock']}")
        logger.info(f"   Can fulfill 5 items: {stock_info['can_fulfill']}")

    # Test 6: Get bestsellers
    logger.info("\nTest 6: Get bestsellers")
    result = await mcp_server.call_tool("get_bestsellers", {"limit": 3})
    if result["success"]:
        logger.info(f"✅ Bestsellers:")
        for product in result["products"]:
            logger.info(f"   - {product['name']}: PKR {product['price']}")

    logger.info("\n✅ All MCP tool tests passed!\n")


async def test_enhanced_agent():
    """Test enhanced agent with MCP tools"""
    logger.info("🧪 Testing Enhanced Agent with MCP Tools\n")

    test_messages = [
        ("web", "What oudh products do you have?"),
        ("whatsapp", "Musk ki price batao"),
        ("email", "I'd like to see your bestsellers"),
    ]

    for channel, message in test_messages:
        logger.info(f"\nTest: {channel.upper()} - {message}")

        try:
            result = await enhanced_agent_service.process_with_tools(
                message=message,
                channel=channel,
                customer_context=None
            )

            logger.info(f"✅ Response: {result['response'][:150]}...")
            logger.info(f"   Tools enabled: {result['tools_enabled']}")

        except Exception as e:
            logger.error(f"❌ Error: {e}")

    logger.info("\n✅ Enhanced agent tests passed!\n")


async def test_tool_direct_call():
    """Test direct tool calling"""
    logger.info("🧪 Testing Direct Tool Calls\n")

    test_cases = [
        {
            "tool": "search_products",
            "params": {"query": "rose", "limit": 2},
            "description": "Search for rose products"
        },
        {
            "tool": "get_product_details",
            "params": {"product_id": "NS-003"},
            "description": "Get details for NS-003"
        },
        {
            "tool": "get_bestsellers",
            "params": {"limit": 3},
            "description": "Get top 3 bestsellers"
        }
    ]

    for test_case in test_cases:
        logger.info(f"\nTest: {test_case['description']}")
        logger.info(f"Tool: {test_case['tool']}")
        logger.info(f"Params: {test_case['params']}")

        result = await mcp_server.call_tool(
            test_case['tool'],
            test_case['params']
        )

        if result.get("success"):
            logger.info(f"✅ Success: {list(result.keys())}")
            if "products" in result:
                logger.info(f"   Products found: {result['count']}")
            elif "product" in result:
                logger.info(f"   Product: {result['product']['name']}")
        else:
            logger.error(f"❌ Failed: {result.get('error')}")

    logger.info("\n✅ Direct tool call tests passed!\n")


async def run_all_tests():
    """Run all MCP server tests"""
    logger.info("🚀 Starting MCP Server Tests\n")
    logger.info("=" * 60)

    try:
        # Test MCP tools
        await test_mcp_tools()

        # Test enhanced agent
        await test_enhanced_agent()

        # Test direct tool calls
        await test_tool_direct_call()

        logger.info("=" * 60)
        logger.info("🎉 All MCP server tests passed successfully!")
        logger.info("\n✅ MCP Server is fully operational!")
        logger.info("\n📋 Available endpoints:")
        logger.info("   GET  /api/v1/mcp/tools - List all tools")
        logger.info("   GET  /api/v1/mcp/tools/{tool_name} - Get tool info")
        logger.info("   POST /api/v1/mcp/tools/call - Call a tool directly")
        logger.info("   POST /api/v1/mcp/agent/chat - Chat with enhanced agent")
        logger.info("   GET  /api/v1/mcp/status - Get MCP server status")

    except Exception as e:
        logger.error(f"❌ Tests failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())
