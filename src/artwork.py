import random

def generate_sakura_tree():
    elements = []
    
    styles = """
    <style>
        @keyframes sway {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            50% { transform: translate(5px, 8px) rotate(5deg); }
        }
        @keyframes floatDown {
            0% { transform: translate(0, -20px) rotate(0deg); opacity: 0; }
            10% { opacity: 0.7; }
            90% { opacity: 0.7; }
            100% { transform: translate(80px, 350px) rotate(90deg); opacity: 0; }
        }
        @keyframes floatCloud {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(15px, 0); }
        }
        .petal { transform-origin: center; }
        .animated-sway { animation: sway 6s ease-in-out infinite; }
        .animated-fall { animation: floatDown 15s linear infinite; }
        .animated-cloud { animation: floatCloud 20s ease-in-out infinite; }
    </style>
    """
    
    # 1. Background Sky/Mist (subtle gradients or paths)
    elements.append('<path d="M 0,350 Q 300,290 600,350 Q 900,290 1200,350 L 1200,350 L 0,350 Z" fill="#F9F5F7" opacity="0.8"/>')
    
    # 2. Sun (Soft, upper middle)
    elements.append('<circle cx="600" cy="180" r="100" fill="#FFF0F5" opacity="0.6"/>')
    
    # 3. Clouds
    elements.append('<g class="animated-cloud" fill="#FFFFFF" opacity="0.5">')
    elements.append('<path d="M 200,80 Q 220,60 240,80 Q 270,70 290,90 Q 310,90 320,110 L 180,110 Q 170,90 200,80 Z"/>')
    elements.append('</g>')
    
    # 4. Mountains (Bottom left, very subtle)
    elements.append('<path d="M -50,350 L 100,220 L 250,350 Z" fill="#E8DDE1" opacity="0.6"/>')
    elements.append('<path d="M 50,350 L 180,260 L 320,350 Z" fill="#D6C6CB" opacity="0.5"/>')
    
    # 5. Pagoda (Subtle in lower left)
    pagoda = """
    <g transform="translate(60, 270) scale(0.8)" fill="#8A7A80" opacity="0.4">
        <!-- Base -->
        <rect x="-20" y="70" width="40" height="20"/>
        <!-- Level 1 -->
        <path d="M -30,70 L 30,70 L 25,60 L -25,60 Z"/>
        <rect x="-15" y="45" width="30" height="15"/>
        <!-- Roof 1 -->
        <path d="M -35,45 Q -15,35 0,35 Q 15,35 35,45 L 20,40 L -20,40 Z"/>
        <!-- Level 2 -->
        <rect x="-10" y="25" width="20" height="15"/>
        <!-- Roof 2 -->
        <path d="M -25,25 Q -10,18 0,18 Q 10,18 25,25 L 15,20 L -15,20 Z"/>
        <!-- Level 3 -->
        <rect x="-6" y="10" width="12" height="10"/>
        <!-- Roof 3 -->
        <path d="M -15,10 Q -5,5 0,5 Q 5,5 15,10 L 10,7 L -10,7 Z"/>
        <!-- Spire -->
        <line x1="0" y1="5" x2="0" y2="-15" stroke="#8A7A80" stroke-width="2"/>
    </g>
    """
    elements.append(pagoda)

    # 6. Sakura Tree (Entering from Upper-Left, avoiding grid > X=200 & Y=140)
    branches = [
        # Main trunk from top-left corner
        '<path d="M -20,-20 Q 50,50 120,120" stroke="#3D2930" stroke-width="14" fill="none" stroke-linecap="round"/>',
        # Branch going slightly down but stopping at X=160
        '<path d="M 40,40 Q 80,100 160,110" stroke="#3D2930" stroke-width="8" fill="none" stroke-linecap="round"/>',
        # Branch staying high, going right to X=250 but Y=50 (above grid)
        '<path d="M 60,60 Q 150,20 250,40" stroke="#3D2930" stroke-width="6" fill="none" stroke-linecap="round"/>',
        # Higher branch
        '<path d="M 20,10 Q 100,0 180,20" stroke="#3D2930" stroke-width="5" fill="none" stroke-linecap="round"/>',
        # Extra small twigs
        '<path d="M 100,105 Q 130,140 140,160" stroke="#3D2930" stroke-width="3" fill="none" stroke-linecap="round"/>',
        '<path d="M 180,30 Q 230,10 280,15" stroke="#3D2930" stroke-width="3" fill="none" stroke-linecap="round"/>'
    ]
    elements.extend(branches)
    
    # 7. Blossoms (Clustered on branches)
    petal_path = "M 0,0 C 2,-5 6,-5 7,-2 C 5,1 0,5 0,5 C 0,5 -5,1 -7,-2 C -6,-5 -2,-5 0,0 Z"
    blossom_colors = ["#FBC4D6", "#F58EB7", "#FDF6F8", "#E84C8F"]
    
    clusters = [
        (40, 40), (80, 80), (120, 120), (160, 110), (100, 105), (140, 160),
        (60, 60), (120, 40), (200, 30), (250, 40), (20, 10), (100, 10), (180, 20), (280, 15)
    ]
    
    for cx, cy in clusters:
        for _ in range(7):
            x = cx + random.randint(-20, 20)
            y = cy + random.randint(-20, 20)
            scale = random.uniform(0.6, 1.2)
            delay = random.uniform(0, 5)
            color = random.choice(blossom_colors)
            elements.append(
                f'<path class="petal animated-sway" style="animation-delay: {delay}s;" '
                f'd="{petal_path}" fill="{color}" opacity="0.85" '
                f'transform="translate({x}, {y}) scale({scale})"/>'
            )

    # 8. Falling Petals (Scattered across whole canvas but not obstructive)
    for i in range(20):
        x = random.randint(50, 1150)
        y = random.randint(-50, 100)
        duration = random.uniform(14, 25)
        delay = random.uniform(0, 20)
        scale = random.uniform(0.5, 0.9)
        color = random.choice(blossom_colors)
        elements.append(
            f'<g class="animated-fall" style="animation-duration: {duration}s; animation-delay: {delay}s;">'
            f'<path d="{petal_path}" fill="{color}" opacity="0.6" transform="translate({x}, {y}) scale({scale})"/>'
            f'</g>'
        )
        
    return styles + "".join(elements)
