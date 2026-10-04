import random

def generate_sakura_tree():
    elements = []
    
    styles = """
    <style>
        @keyframes sway {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            50% { transform: translate(10px, 15px) rotate(15deg); }
        }
        @keyframes floatDown {
            0% { transform: translate(0, -20px) rotate(0deg); opacity: 0; }
            10% { opacity: 0.8; }
            90% { opacity: 0.8; }
            100% { transform: translate(60px, 350px) rotate(60deg); opacity: 0; }
        }
        @keyframes floatCloud {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(20px, 0); }
        }
        .petal { transform-origin: center; }
        .animated-sway { animation: sway 6s ease-in-out infinite; }
        .animated-fall { animation: floatDown 15s linear infinite; }
        .animated-cloud { animation: floatCloud 20s ease-in-out infinite; }
    </style>
    """
    
    # 1. Background Sky/Mist (subtle gradients or paths)
    elements.append('<path d="M 0,350 Q 300,280 600,350 Q 900,280 1200,350 L 1200,350 L 0,350 Z" fill="#F4EFF2" opacity="0.6"/>')
    
    # 2. Sun
    elements.append('<circle cx="1000" cy="120" r="50" fill="#FFEAEF" opacity="0.8"/>')
    
    # 3. Clouds
    elements.append('<g class="animated-cloud" fill="#FFFFFF" opacity="0.6">')
    elements.append('<path d="M 850,100 Q 870,80 890,100 Q 920,90 940,110 Q 960,110 970,130 L 830,130 Q 820,110 850,100 Z"/>')
    elements.append('</g>')
    
    elements.append('<g class="animated-cloud" style="animation-delay: -10s;" fill="#FFFFFF" opacity="0.5">')
    elements.append('<path d="M 1050,150 Q 1070,130 1090,150 Q 1120,140 1140,160 Q 1160,160 1170,180 L 1030,180 Q 1020,160 1050,150 Z"/>')
    elements.append('</g>')
    
    # 4. Mountains
    # Back mountain
    elements.append('<path d="M -100,350 L 150,150 L 450,350 Z" fill="#E8DDE1" opacity="0.7"/>')
    # Front mountain
    elements.append('<path d="M 50,350 L 250,200 L 550,350 Z" fill="#D6C6CB" opacity="0.8"/>')
    
    # 5. Water / Ground
    elements.append('<path d="M 0,330 Q 300,320 600,330 Q 900,340 1200,330 L 1200,350 L 0,350 Z" fill="#D2E1E6" opacity="0.5"/>')
    elements.append('<path d="M 0,340 Q 300,330 600,340 Q 900,350 1200,340 L 1200,350 L 0,350 Z" fill="#C2D6DD" opacity="0.6"/>')

    # 6. Pagoda (Bottom Left/Center-left)
    pagoda = """
    <g transform="translate(180, 260)" fill="#3A2F33">
        <!-- Base -->
        <rect x="-20" y="70" width="40" height="20" fill="#2C2427"/>
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
        <line x1="0" y1="5" x2="0" y2="-15" stroke="#3A2F33" stroke-width="2"/>
        <circle cx="0" cy="-10" r="3" fill="#3A2F33"/>
        <circle cx="0" cy="-15" r="2" fill="#3A2F33"/>
    </g>
    """
    elements.append(pagoda)

    # 7. Sakura Tree (Left side, spanning top)
    branches = [
        '<path d="M -30,350 Q -10,200 50,50 Q 200,20 350,10" stroke="#2B1A1E" stroke-width="12" fill="none" stroke-linecap="round"/>',
        '<path d="M -10,250 Q 80,180 180,100" stroke="#2B1A1E" stroke-width="8" fill="none" stroke-linecap="round"/>',
        '<path d="M 50,130 Q 150,120 250,50" stroke="#2B1A1E" stroke-width="6" fill="none" stroke-linecap="round"/>',
        '<path d="M 120,80 Q 220,100 280,30" stroke="#2B1A1E" stroke-width="4" fill="none" stroke-linecap="round"/>',
        '<path d="M 180,100 Q 280,150 380,80" stroke="#2B1A1E" stroke-width="4" fill="none" stroke-linecap="round"/>',
        '<path d="M 250,50 Q 350,60 450,20" stroke="#2B1A1E" stroke-width="3" fill="none" stroke-linecap="round"/>'
    ]
    elements.extend(branches)
    
    # 8. Blossoms (Static and Swaying)
    petal_path = "M 0,0 C 2,-5 6,-5 7,-2 C 5,1 0,5 0,5 C 0,5 -5,1 -7,-2 C -6,-5 -2,-5 0,0 Z"
    blossom_colors = ["#FBC4D6", "#F58EB7", "#FDF6F8"]
    
    # Generate clusters along branches
    clusters = [
        (50, 50), (100, 30), (150, 70), (200, 20), (250, 50), 
        (300, 10), (350, 60), (400, 30), (450, 20), (180, 100),
        (230, 120), (280, 140), (330, 100), (380, 80), (120, 80), (80, 180)
    ]
    
    for cx, cy in clusters:
        for _ in range(8):
            x = cx + random.randint(-25, 25)
            y = cy + random.randint(-25, 25)
            scale = random.uniform(0.6, 1.4)
            delay = random.uniform(0, 5)
            color = random.choice(blossom_colors)
            elements.append(
                f'<path class="petal animated-sway" style="animation-delay: {delay}s;" '
                f'd="{petal_path}" fill="{color}" opacity="0.9" '
                f'transform="translate({x}, {y}) scale({scale})"/>'
            )

    # 9. Falling Petals
    for i in range(25):
        x = random.randint(300, 1150)
        y = random.randint(-50, 50)
        duration = random.uniform(12, 22)
        delay = random.uniform(0, 20)
        scale = random.uniform(0.5, 1.1)
        color = random.choice(blossom_colors)
        elements.append(
            f'<g class="animated-fall" style="animation-duration: {duration}s; animation-delay: {delay}s;">'
            f'<path d="{petal_path}" fill="{color}" opacity="0.8" transform="translate({x}, {y}) scale({scale})"/>'
            f'</g>'
        )
        
    return styles + "".join(elements)
