"""
Optional HTTP Server for LeaseWatch
This file can be used if you need to expose LeaseWatch as a web service
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime
from aiohttp import web, web_request
from aiohttp.web_response import Response

from main import main as leasewatch_main
from src.utils.logger import Logger
from src.services.storage import default_storage
from src.services.report import default_report_service

logger = Logger("LeaseWatchServer")

# Server configuration
PORT = 8000
HOST = "localhost"


async def health_check(request: web_request.Request) -> Response:
    """Health check endpoint"""
    return web.json_response({
        'status': 'healthy',
        'service': 'LeaseWatch',
        'timestamp': datetime.now().isoformat()
    })


async def run_scraping(request: web_request.Request) -> Response:
    """Endpoint to trigger scraping"""
    try:
        logger.info('🌐 HTTP request received to start scraping...')
        
        # Run the main scraping function
        await leasewatch_main()
        
        return web.json_response({
            'success': True,
            'message': 'Scraping completed successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as error:
        logger.error(f'❌ Scraping failed: {str(error)}')
        return web.json_response({
            'success': False,
            'message': str(error),
            'timestamp': datetime.now().isoformat()
        }, status=500)


async def get_latest_data(request: web_request.Request) -> Response:
    """Get the latest scraped data"""
    try:
        # Get query parameters
        date_str = request.query.get('date')  # Optional date parameter
        
        # Load data
        floor_plans = default_storage.load_daily_data(date_str)
        
        if not floor_plans:
            return web.json_response({
                'success': False,
                'message': f'No data found for date: {date_str or "today"}',
                'data': []
            }, status=404)
        
        # Convert to JSON-serializable format
        data = [fp.model_dump() for fp in floor_plans]
        
        return web.json_response({
            'success': True,
            'message': f'Retrieved {len(floor_plans)} floor plans',
            'date': date_str or datetime.now().date().isoformat(),
            'data': data
        })
        
    except Exception as error:
        logger.error(f'❌ Error retrieving data: {str(error)}')
        return web.json_response({
            'success': False,
            'message': str(error)
        }, status=500)


async def get_report(request: web_request.Request) -> Response:
    """Get daily report"""
    try:
        # Get query parameters
        date_str = request.query.get('date')  # Optional date parameter
        report_type = request.query.get('type', 'daily')  # Type of report
        
        # Load floor plans
        floor_plans = default_storage.load_daily_data(date_str)
        
        if not floor_plans:
            return web.json_response({
                'success': False,
                'message': f'No data found for date: {date_str or "today"}'
            }, status=404)
        
        # Generate report based on type
        if report_type == 'daily':
            report_content = default_report_service.generate_executive_summary(floor_plans, [])
        elif report_type == 'comparison':
            report_content = default_report_service.generate_property_comparison_report(floor_plans)
        elif report_type == 'bedroom':
            report_content = default_report_service.generate_bedroom_analysis_report(floor_plans)
        elif report_type == 'availability':
            report_content = default_report_service.generate_availability_report(floor_plans)
        else:
            return web.json_response({
                'success': False,
                'message': 'Invalid report type. Use: daily, comparison, bedroom, or availability'
            }, status=400)
        
        return web.json_response({
            'success': True,
            'report_type': report_type,
            'date': date_str or datetime.now().date().isoformat(),
            'content': report_content
        })
        
    except Exception as error:
        logger.error(f'❌ Error generating report: {str(error)}')
        return web.json_response({
            'success': False,
            'message': str(error)
        }, status=500)


async def get_available_dates(request: web_request.Request) -> Response:
    """Get list of available data dates"""
    try:
        dates = default_storage.get_available_dates()
        
        return web.json_response({
            'success': True,
            'message': f'Found {len(dates)} available dates',
            'dates': dates
        })
        
    except Exception as error:
        logger.error(f'❌ Error retrieving available dates: {str(error)}')
        return web.json_response({
            'success': False,
            'message': str(error)
        }, status=500)


async def get_property_history(request: web_request.Request) -> Response:
    """Get historical data for a specific property"""
    try:
        property_name = request.query.get('property')
        days = int(request.query.get('days', 30))
        
        if not property_name:
            return web.json_response({
                'success': False,
                'message': 'Property name is required'
            }, status=400)
        
        history = default_storage.get_property_history(property_name, days)
        
        return web.json_response({
            'success': True,
            'property': property_name,
            'days': days,
            'history': history
        })
        
    except Exception as error:
        logger.error(f'❌ Error retrieving property history: {str(error)}')
        return web.json_response({
            'success': False,
            'message': str(error)
        }, status=500)


async def init_app() -> web.Application:
    """Initialize the web application"""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/health', health_check)
    app.router.add_post('/scrape', run_scraping)
    app.router.add_get('/data', get_latest_data)
    app.router.add_get('/report', get_report)
    app.router.add_get('/dates', get_available_dates)
    app.router.add_get('/history', get_property_history)
    
    # Add a simple index route
    async def index(request: web_request.Request) -> Response:
        return web.json_response({
            'service': 'LeaseWatch',
            'version': '1.0.0',
            'description': 'Automated Apartment Pricing Tracker',
            'endpoints': {
                'GET /health': 'Health check',
                'POST /scrape': 'Trigger apartment data scraping',
                'GET /data': 'Get latest scraped data (optional ?date=YYYY-MM-DD)',
                'GET /report': 'Get reports (optional ?type=daily|comparison|bedroom|availability&date=YYYY-MM-DD)',
                'GET /dates': 'Get available data dates',
                'GET /history': 'Get property history (required ?property=name&days=30)'
            }
        })
    
    app.router.add_get('/', index)
    
    return app


async def main():
    """Main function to run the HTTP server"""
    logger.info(f'🌐 Starting LeaseWatch HTTP server on http://{HOST}:{PORT}')
    
    app = await init_app()
    
    # Create and start the server
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    
    logger.info('🌐 LeaseWatch server running!')
    logger.info('Available endpoints:')
    logger.info(f'  - GET  http://{HOST}:{PORT}/')
    logger.info(f'  - GET  http://{HOST}:{PORT}/health')
    logger.info(f'  - POST http://{HOST}:{PORT}/scrape')
    logger.info(f'  - GET  http://{HOST}:{PORT}/data')
    logger.info(f'  - GET  http://{HOST}:{PORT}/report')
    logger.info(f'  - GET  http://{HOST}:{PORT}/dates')
    logger.info(f'  - GET  http://{HOST}:{PORT}/history')
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info('🛑 Shutting down LeaseWatch server...')
    finally:
        await runner.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
