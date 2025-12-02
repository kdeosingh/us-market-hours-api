"""
Custom API documentation with authentication
"""
from fastapi import APIRouter, Request, Form, HTTPException, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
import secrets
from typing import Optional

from app.config import settings

router = APIRouter()

# Store sessions in memory (use Redis in production)
active_sessions = {}

def get_session_token(request: Request) -> Optional[str]:
    """Get session token from cookie"""
    return request.cookies.get("docs_session")

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    token = get_session_token(request)
    if not token:
        return False
    
    session = active_sessions.get(token)
    if not session:
        return False
    
    # Check if session expired (24 hours)
    if datetime.now() > session["expires"]:
        del active_sessions[token]
        return False
    
    return True

def require_auth(request: Request):
    """Dependency to require authentication"""
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.get("/login", response_class=HTMLResponse)
async def docs_login_page(request: Request):
    """Login page for API documentation"""
    
    # If already authenticated, redirect to docs
    if is_authenticated(request):
        return RedirectResponse(url="/documentation", status_code=302)
    
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation Login - US Market Hours</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .login-container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 440px;
            padding: 48px;
            animation: slideUp 0.4s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .logo {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
        }
        
        .logo svg {
            width: 32px;
            height: 32px;
            color: white;
        }
        
        h1 {
            text-align: center;
            color: #1a202c;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .subtitle {
            text-align: center;
            color: #718096;
            font-size: 14px;
            margin-bottom: 32px;
        }
        
        .form-group {
            margin-bottom: 24px;
        }
        
        label {
            display: block;
            color: #4a5568;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        input[type="password"] {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 15px;
            transition: all 0.2s;
            font-family: inherit;
        }
        
        input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .error {
            background: #fee;
            border: 1px solid #fcc;
            color: #c33;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            text-align: center;
        }
        
        .info-box {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin-top: 24px;
        }
        
        .info-box h3 {
            color: #2d3748;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .info-box p {
            color: #718096;
            font-size: 13px;
            line-height: 1.6;
        }
        
        .info-box code {
            background: #edf2f7;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
        </div>
        
        <h1>API Documentation</h1>
        <p class="subtitle">Enter password to access interactive docs</p>
        
        <form method="post" action="/documentation/verify">
            <div class="form-group">
                <label for="password">Password</label>
                <input 
                    type="password" 
                    id="password" 
                    name="password" 
                    placeholder="Enter documentation password"
                    autocomplete="off"
                    required
                    autofocus
                >
            </div>
            
            <button type="submit">Access Documentation</button>
        </form>
        
        <div class="info-box">
            <h3>🔒 Secure Access</h3>
            <p>
                This documentation is password-protected for authorized users only.
                Configure the password in <code>backend/.env</code> with <code>DOCS_PASSWORD</code>.
            </p>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html)


@router.post("/verify")
async def verify_docs_password(password: str = Form(...)):
    """Verify password and create session"""
    
    if password != settings.DOCS_PASSWORD:
        # Redirect back with error
        return RedirectResponse(url="/documentation/login?error=invalid", status_code=302)
    
    # Create session token
    token = secrets.token_urlsafe(32)
    active_sessions[token] = {
        "created": datetime.now(),
        "expires": datetime.now() + timedelta(hours=24)
    }
    
    # Redirect to docs with session cookie
    response = RedirectResponse(url="/documentation", status_code=302)
    response.set_cookie(
        key="docs_session",
        value=token,
        httponly=True,
        max_age=86400,  # 24 hours
        samesite="lax"
    )
    
    return response


@router.get("/logout")
async def docs_logout(request: Request):
    """Logout from documentation"""
    token = get_session_token(request)
    if token and token in active_sessions:
        del active_sessions[token]
    
    response = RedirectResponse(url="/documentation/login", status_code=302)
    response.delete_cookie("docs_session")
    return response


@router.get("", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def api_documentation(request: Request):
    """Beautiful custom API documentation"""
    
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - US Market Hours Calendar</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f7fafc;
            color: #2d3748;
            line-height: 1.6;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 32px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 32px;
            font-weight: 700;
        }
        
        .header p {
            opacity: 0.9;
            margin-top: 4px;
        }
        
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.2s;
        }
        
        .logout-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 24px;
        }
        
        .intro-section {
            background: white;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 32px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .intro-section h2 {
            color: #1a202c;
            font-size: 24px;
            margin-bottom: 16px;
        }
        
        .base-url {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            padding: 16px;
            border-radius: 8px;
            margin: 16px 0;
        }
        
        .base-url code {
            color: #667eea;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 14px;
        }
        
        .endpoint-section {
            background: white;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .endpoint-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .method {
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.5px;
        }
        
        .method.get {
            background: #d4edda;
            color: #155724;
        }
        
        .method.post {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .endpoint-path {
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 16px;
            color: #1a202c;
            font-weight: 600;
        }
        
        .description {
            color: #4a5568;
            margin-bottom: 20px;
            font-size: 15px;
        }
        
        .code-block {
            background: #1a202c;
            color: #f7fafc;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 16px 0;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
        }
        
        .code-block .key {
            color: #81e6d9;
        }
        
        .code-block .string {
            color: #f687b3;
        }
        
        .code-block .number {
            color: #feb2b2;
        }
        
        .code-block .boolean {
            color: #fbd38d;
        }
        
        .params-table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
        }
        
        .params-table th {
            background: #f7fafc;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #e2e8f0;
            font-size: 13px;
            color: #4a5568;
        }
        
        .params-table td {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }
        
        .params-table code {
            background: #f7fafc;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .badge.required {
            background: #fee;
            color: #c33;
        }
        
        .badge.optional {
            background: #f0f9ff;
            color: #0369a1;
        }
        
        h3 {
            color: #1a202c;
            font-size: 18px;
            margin: 24px 0 12px;
        }
        
        .try-it {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            margin-top: 16px;
            transition: transform 0.2s;
        }
        
        .try-it:hover {
            transform: translateY(-2px);
        }
        
        .footer {
            text-align: center;
            padding: 40px 24px;
            color: #718096;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div>
                <h1>📊 US Market Hours Calendar API</h1>
                <p>Real-time US stock market hours and holiday schedules</p>
            </div>
            <a href="/documentation/logout" class="logout-btn">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="intro-section">
            <h2>Getting Started</h2>
            <p>Welcome to the US Market Hours Calendar API documentation. This API provides real-time information about NYSE and NASDAQ trading hours, including regular hours, early closes, and holiday schedules.</p>
            
            <div class="base-url">
                <strong>Base URL:</strong> <code>http://localhost:8000</code>
            </div>
            
            <p style="margin-top: 16px;">All times are returned in <strong>UTC format</strong> for consistency. You can convert them to any timezone on the client side.</p>
        </div>
        
        <!-- GET Today's Market Hours -->
        <div class="endpoint-section">
            <div class="endpoint-header">
                <span class="method get">GET</span>
                <span class="endpoint-path">/market-hours/today</span>
            </div>
            
            <p class="description">Get today's market open/close times, status, and notes.</p>
            
            <h3>Response Example</h3>
            <div class="code-block">
{
  <span class="key">"date"</span>: <span class="string">"2025-11-28"</span>,
  <span class="key">"open_time_utc"</span>: <span class="string">"2025-11-28T14:30:00+00:00"</span>,
  <span class="key">"close_time_utc"</span>: <span class="string">"2025-11-28T18:00:00+00:00"</span>,
  <span class="key">"is_open"</span>: <span class="boolean">true</span>,
  <span class="key">"is_early_close"</span>: <span class="boolean">true</span>,
  <span class="key">"notes"</span>: <span class="string">"Day after Thanksgiving"</span>,
  <span class="key">"status"</span>: <span class="string">"EARLY_CLOSE"</span>
}
            </div>
            
            <button class="try-it" onclick="window.open('/market-hours/today', '_blank')">Try it →</button>
        </div>
        
        <!-- GET 7-Day Schedule -->
        <div class="endpoint-section">
            <div class="endpoint-header">
                <span class="method get">GET</span>
                <span class="endpoint-path">/market-hours/week</span>
            </div>
            
            <p class="description">Get 7-day market schedule starting from today or a specified date.</p>
            
            <h3>Query Parameters</h3>
            <table class="params-table">
                <thead>
                    <tr>
                        <th>Parameter</th>
                        <th>Type</th>
                        <th>Required</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>start_date</code></td>
                        <td>string</td>
                        <td><span class="badge optional">Optional</span></td>
                        <td>Start date in YYYY-MM-DD format</td>
                    </tr>
                </tbody>
            </table>
            
            <h3>Response Example</h3>
            <div class="code-block">
{
  <span class="key">"start_date"</span>: <span class="string">"2025-11-28"</span>,
  <span class="key">"end_date"</span>: <span class="string">"2025-12-04"</span>,
  <span class="key">"days"</span>: [
    {
      <span class="key">"date"</span>: <span class="string">"2025-11-28"</span>,
      <span class="key">"is_open"</span>: <span class="boolean">true</span>,
      <span class="key">"is_early_close"</span>: <span class="boolean">true</span>,
      <span class="key">"status"</span>: <span class="string">"EARLY_CLOSE"</span>
    }
    <span class="comment">// ... 6 more days</span>
  ]
}
            </div>
            
            <button class="try-it" onclick="window.open('/market-hours/week', '_blank')">Try it →</button>
        </div>
        
        <!-- GET Next Market Event -->
        <div class="endpoint-section">
            <div class="endpoint-header">
                <span class="method get">GET</span>
                <span class="endpoint-path">/market-hours/next</span>
            </div>
            
            <p class="description">Get the next market open or close event with countdown timer.</p>
            
            <h3>Response Example</h3>
            <div class="code-block">
{
  <span class="key">"event_type"</span>: <span class="string">"close"</span>,
  <span class="key">"event_time_utc"</span>: <span class="string">"2025-11-28T18:00:00+00:00"</span>,
  <span class="key">"time_until_seconds"</span>: <span class="number">3600</span>,
  <span class="key">"next_date"</span>: <span class="string">"2025-11-28"</span>,
  <span class="key">"is_early_close"</span>: <span class="boolean">true</span>,
  <span class="key">"notes"</span>: <span class="string">"Day after Thanksgiving"</span>
}
            </div>
            
            <button class="try-it" onclick="window.open('/market-hours/next', '_blank')">Try it →</button>
        </div>
        
        <!-- GET Specific Date -->
        <div class="endpoint-section">
            <div class="endpoint-header">
                <span class="method get">GET</span>
                <span class="endpoint-path">/market-hours/date/{date}</span>
            </div>
            
            <p class="description">Get market hours for a specific date.</p>
            
            <h3>Path Parameters</h3>
            <table class="params-table">
                <thead>
                    <tr>
                        <th>Parameter</th>
                        <th>Type</th>
                        <th>Required</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>date</code></td>
                        <td>string</td>
                        <td><span class="badge required">Required</span></td>
                        <td>Date in YYYY-MM-DD format (e.g., 2025-12-25)</td>
                    </tr>
                </tbody>
            </table>
            
            <button class="try-it" onclick="window.open('/market-hours/date/2025-12-25', '_blank')">Try it (Christmas) →</button>
        </div>
        
        <!-- Check If Open -->
        <div class="endpoint-section">
            <div class="endpoint-header">
                <span class="method get">GET</span>
                <span class="endpoint-path">/market-hours/is-open</span>
            </div>
            
            <p class="description">Quick check if market is currently open (boolean response).</p>
            
            <h3>Response Example</h3>
            <div class="code-block">
{
  <span class="key">"is_open"</span>: <span class="boolean">true</span>,
  <span class="key">"message"</span>: <span class="string">"Market open"</span>,
  <span class="key">"timestamp"</span>: <span class="string">"2025-11-28T16:30:00+00:00"</span>
}
            </div>
            
            <button class="try-it" onclick="window.open('/market-hours/is-open', '_blank')">Try it →</button>
        </div>
        
        <!-- Status Codes -->
        <div class="endpoint-section">
            <h2>Status Codes</h2>
            <table class="params-table">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>200</code></td>
                        <td>Success - Request completed successfully</td>
                    </tr>
                    <tr>
                        <td><code>400</code></td>
                        <td>Bad Request - Invalid parameters</td>
                    </tr>
                    <tr>
                        <td><code>404</code></td>
                        <td>Not Found - Resource not found</td>
                    </tr>
                    <tr>
                        <td><code>500</code></td>
                        <td>Server Error - Internal server error</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- Market Status Values -->
        <div class="endpoint-section">
            <h2>Market Status Values</h2>
            <table class="params-table">
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>OPEN</code></td>
                        <td>Market is open for regular trading (9:30 AM - 4:00 PM ET)</td>
                    </tr>
                    <tr>
                        <td><code>EARLY_CLOSE</code></td>
                        <td>Market closes early at 1:00 PM ET</td>
                    </tr>
                    <tr>
                        <td><code>CLOSED</code></td>
                        <td>Market is closed (holiday, weekend, or outside hours)</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <p>US Market Hours Calendar API v1.0.0</p>
        <p style="margin-top: 8px;">Data updates daily at 6:00 AM UTC</p>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html)




