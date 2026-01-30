"""Improved SVG Architecture Diagram Generator"""

from typing import List, Dict, Any


def generate_architecture_svg(services: List[str]) -> str:
    """
    Generate Azure architecture diagram with visible arrows and proper flows

    Args:
        services: List of service names

    Returns:
        SVG markup with detailed architecture layout including arrows
    """
    # Categorize services
    internet_facing = []
    load_balancers = []
    app_tier = []
    data_tier = []
    security_tier = []
    monitoring_tier = []

    for service in services:
        s_lower = service.lower()
        if 'gateway' in s_lower or 'cdn' in s_lower or 'front door' in s_lower:
            internet_facing.append(service)
        elif 'load balancer' in s_lower or 'traffic manager' in s_lower:
            load_balancers.append(service)
        elif any(w in s_lower for w in ['app service', 'function', 'aks', 'container', 'virtual machine', 'vm', 'web']):
            app_tier.append(service)
        elif any(w in s_lower for w in ['sql', 'cosmos', 'database', 'storage', 'blob', 'data lake']):
            data_tier.append(service)
        elif any(w in s_lower for w in ['key vault', 'security', 'defender']):
            security_tier.append(service)
        elif any(w in s_lower for w in ['insights', 'monitor', 'log', 'analytics']):
            monitoring_tier.append(service)
        else:
            app_tier.append(service)

    width = 1000
    height = 700

    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
    </marker>
    <marker id="arrow-gray" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#666" />
    </marker>
    <linearGradient id="boxGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#FFE600;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#FFD700;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>

  <style>
    .service-box {{ fill: url(#boxGradient); stroke: #2E2E38; stroke-width: 2.5; filter: url(#shadow); }}
    .service-text {{ fill: #2E2E38; font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 13px; font-weight: 600; }}
    .service-icon {{ fill: #2E2E38; font-family: 'Segoe UI', sans-serif; font-size: 20px; }}
    .layer-label {{ fill: #1976d2; font-family: 'Segoe UI', sans-serif; font-size: 15px; font-weight: 700; text-transform: uppercase; }}
    .title-text {{ fill: #1a1a1a; font-family: 'Segoe UI', sans-serif; font-size: 24px; font-weight: bold; }}
    .vnet-border {{ fill: none; stroke: #1976d2; stroke-width: 3; stroke-dasharray: 10,5; opacity: 0.6; }}
    .subnet-border {{ fill: #e3f2fd; fill-opacity: 0.2; stroke: #1976d2; stroke-width: 2; stroke-dasharray: 5,3; }}
    .arrow-line {{ stroke: #2563eb; stroke-width: 3; fill: none; marker-end: url(#arrow); }}
    .arrow-bi {{ stroke: #9333ea; stroke-width: 2.5; fill: none; marker-end: url(#arrow); marker-start: url(#arrow); }}
    .connection-light {{ stroke: #666; stroke-width: 1.5; fill: none; stroke-dasharray: 3,3; marker-end: url(#arrow-gray); }}
    .internet-icon {{ fill: #3b82f6; }}
    .security-box {{ fill: #fef3c7; stroke: #f59e0b; stroke-width: 2; }}
  </style>

  <!-- Title -->
  <text x="{width/2}" y="35" class="title-text" text-anchor="middle">Azure Infrastructure Architecture</text>

  <!-- Azure Cloud Border -->
  <rect x="20" y="70" width="{width-40}" height="{height-90}" class="vnet-border" rx="15"/>
  <text x="40" y="95" class="layer-label">Azure Cloud</text>

  <!-- Internet -->
  <g transform="translate({width/2 - 40}, 120)">
    <circle cx="40" cy="20" r="25" class="internet-icon" opacity="0.2"/>
    <text x="40" y="27" class="service-icon" text-anchor="middle">🌐</text>
    <text x="40" y="55" class="service-text" text-anchor="middle" font-size="11">Internet</text>
  </g>
'''

    y = 220
    components = []

    # Internet-facing layer
    if internet_facing or load_balancers:
        all_edge = internet_facing + load_balancers
        svg += f'  <text x="50" y="{y-15}" class="layer-label">Edge Layer</text>\n'
        svg += f'  <rect x="40" y="{y-10}" width="{width-80}" height="90" class="subnet-border" rx="8"/>\n'

        x_start = (width - len(all_edge) * 140) / 2
        for i, svc in enumerate(all_edge):
            x = x_start + i * 140
            svg += f'''  <g transform="translate({x}, {y})">
    <rect width="120" height="60" class="service-box" rx="8"/>
    <text x="60" y="20" class="service-icon" text-anchor="middle">⚡</text>
    <text x="60" y="45" class="service-text" text-anchor="middle">{svc[:18]}</text>
  </g>\n'''
            components.append({'name': svc, 'x': x + 60, 'y': y, 'layer': 'edge'})

        # Arrow from internet to edge
        svg += f'  <line x1="{width/2}" y1="175" x2="{width/2}" y2="{y-15}" class="arrow-line"/>\n'
        y += 120

    # Application layer
    if app_tier:
        svg += f'  <text x="50" y="{y-15}" class="layer-label">Application Tier</text>\n'
        svg += f'  <rect x="40" y="{y-10}" width="{width-80}" height="90" class="subnet-border" rx="8"/>\n'

        x_start = (width - len(app_tier) * 140) / 2
        for i, svc in enumerate(app_tier):
            x = x_start + i * 140
            svg += f'''  <g transform="translate({x}, {y})">
    <rect width="120" height="60" class="service-box" rx="8"/>
    <text x="60" y="20" class="service-icon" text-anchor="middle">⚙️</text>
    <text x="60" y="45" class="service-text" text-anchor="middle">{svc[:18]}</text>
  </g>\n'''
            components.append({'name': svc, 'x': x + 60, 'y': y, 'layer': 'app'})

        # Arrow from edge to app
        if components:
            prev_layer = [c for c in components if c['layer'] == 'edge']
            if prev_layer:
                svg += f'  <line x1="{prev_layer[0]["x"]}" y1="{prev_layer[0]["y"]+60}" x2="{components[-1]["x"]}" y2="{y-15}" class="arrow-line"/>\n'
        y += 120

    # Data layer
    if data_tier:
        svg += f'  <text x="50" y="{y-15}" class="layer-label">Data Tier</text>\n'
        svg += f'  <rect x="40" y="{y-10}" width="{width-80}" height="90" class="subnet-border" rx="8"/>\n'

        x_start = (width - len(data_tier) * 140) / 2
        for i, svc in enumerate(data_tier):
            x = x_start + i * 140
            svg += f'''  <g transform="translate({x}, {y})">
    <rect width="120" height="60" class="service-box" rx="8"/>
    <text x="60" y="20" class="service-icon" text-anchor="middle">💾</text>
    <text x="60" y="45" class="service-text" text-anchor="middle">{svc[:18]}</text>
  </g>\n'''
            components.append({'name': svc, 'x': x + 60, 'y': y, 'layer': 'data'})

        # Bidirectional arrow between app and data
        app_comps = [c for c in components if c['layer'] == 'app']
        if app_comps:
            svg += f'  <line x1="{app_comps[0]["x"]}" y1="{app_comps[0]["y"]+60}" x2="{components[-1]["x"]}" y2="{y-15}" class="arrow-bi"/>\n'

    # Security sidebar
    if security_tier:
        svg += f'''  <g transform="translate({width-220}, 220)">
    <text x="0" y="0" class="layer-label">Security</text>
    <rect x="-10" y="10" width="180" height="{len(security_tier)*70+20}" class="security-box" rx="8"/>
'''
        for i, svc in enumerate(security_tier):
            svg += f'''    <g transform="translate(0, {30 + i*70})">
      <rect width="160" height="50" class="service-box" rx="6"/>
      <text x="80" y="18" class="service-icon" text-anchor="middle">🔒</text>
      <text x="80" y="38" class="service-text" text-anchor="middle" font-size="11">{svc[:20]}</text>
    </g>\n'''
        svg += '  </g>\n'

    # Monitoring sidebar
    if monitoring_tier:
        monitor_y = 220 + (len(security_tier) * 70 + 50 if security_tier else 0)
        svg += f'''  <g transform="translate({width-220}, {monitor_y})">
    <text x="0" y="0" class="layer-label" fill="#059669">Monitoring</text>
'''
        for i, svc in enumerate(monitoring_tier):
            svg += f'''    <g transform="translate(0, {20 + i*60})">
      <rect width="160" height="45" class="service-box" rx="6" opacity="0.85"/>
      <text x="80" y="15" class="service-icon" text-anchor="middle">📊</text>
      <text x="80" y="33" class="service-text" text-anchor="middle" font-size="10">{svc[:20]}</text>
    </g>\n'''
        svg += '  </g>\n'

    svg += '</svg>'
    return svg
