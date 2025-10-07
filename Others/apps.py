from django.apps import AppConfig

class OthersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Others'

    def ready(self):
        # Import models here, not at the top
        from django.db.utils import OperationalError
        from .models import ShoesQuestion, ShoesAnswer

        QUESTION_ANSWERS_MAP = {
                # Running Shoes
                "What purpose are you looking for running shoes for?": [
                    ("allrounder", "All-rounder"),
                    ("race_marathon", "Race/Marathon"),
                    ("trail_running", "Trail running (off-road)"),
                    ("interval_training", "Interval runs/Track workouts"),
                    ("long_distance", "Long distances/Long runs"),
                    ("walking", "Walking shoes")
                ],
                
                "How do you prefer your shoes to fit?": [
                    ("perfect_fit", "The perfect running shoe fit based on my 3D scan"),
                    ("roomy", "Rather roomy, as I prefer more freedom of movement"),
                    ("snug", "Rather snug, as I like my shoes to fit tightly on my foot")
                ],
                
                "On which surface will you mainly be running?": [
                    ("hard_surface", "Hard surface - asphalt, cobblestones, sidewalks"),
                    ("mixed_terrain", "Mixed terrain - a mix of natural and urban paths"),
                    ("asphalt_road", "Asphalt/Road - For regular, firm surfaces"),
                    ("mixed", "Mixed - For varying surfaces")
                ],
                
                "Do you know your foot type or pronation?": [
                    ("scan_analysis", "Analysis based on my 3D scan"),
                    ("neutral", "Neutral foot"),
                    ("overpronation", "Overpronation (excessive inward roll)")
                ],
                
                "Have you ever had any problems or pain while running?": [
                    ("no_problems", "No"),
                    ("knee_problems", "Yes, knee problems"),
                    ("calf_problems", "Yes, calf problems"),
                    ("shin_splints", "Yes, shin splints"),
                    ("plantar_fasciitis", "Yes, plantar fasciitis (heel pain)")
                ],
                
                "What role does cushioning play in relation to stability?": [
                    ("max_cushioning", "Maximum cushioning - Focus on comfort and joint protection"),
                    ("balanced", "Balanced - Good ratio of cushioning and stability"),
                    ("more_stability", "More stability - Focus on control and guidance")
                ],
                
                "Do you prefer a higher sole or a normal to mid-range sole height?": [
                    ("higher_sole", "Higher sole - focus on comfort"),
                    ("normal_mid_sole", "Normal to mid-range sole - focus on natural rolling movement")
                ],
                
                # Trail Running
                "How will you primarily use your trail running shoes?": [
                    ("trails_only", "Only on trails & off-road"),
                    ("hybrid_use", "Mix of trail & road (hybrid use)")
                ],
                
                "Should your shoe be waterproof?": [
                    ("yes_waterproof", "Yes, waterproof and breathable (Gore-Tex or similar membrane)"),
                    ("no_waterproof", "No, lighter and better ventilated")
                ],
                
                "What shaft height should your shoe have?": [
                    ("low", "Low (below the ankle)"),
                    ("mid_high", "Mid/High (ankle-high or above)")
                ],
                
                # Interval Training
                "On which surface do you run your interval training?": [
                    ("track_spikes", "Running track (Spikes)"),
                    ("asphalt_track", "Asphalt/Running track (without spikes)")
                ],
                
                "Which distance do you run in your interval training?": [
                    ("short_distance", "Short distance (100-400 M)"),
                    ("middle_long_distance", "Middle & Long distance (800 M - 10,000 M)")
                ],
                
                # Racing
                "What type of racing shoes are you looking for?": [
                    ("with_carbon", "Racing shoes with carbon"),
                    ("without_carbon", "Racing shoes without carbon")
                ],
                
                "For which distance are you looking for racing shoes?": [
                    ("short_race", "Short distance (5 km - 10 km)"),
                    ("half_marathon", "Half marathon (21.1 km)"),
                    ("marathon", "Marathon (42.2 km & more)")
                ],
                
                "What drop do you prefer?": [
                    ("standard_drop", "6-10 mm - Proven choice, supports the rolling motion"),
                    ("minimal_drop", "≤ 6 mm - Direct push-off, requires trained technique")
                ],
                
                # Cycling Shoes
                "What type of cycling do you do?": [
                    ("road_bike", "Road bike"),
                    ("mountain_bike", "Mountain bike"),
                    ("gravel", "Gravel")
                ],
                
                "What type of pedals do you use?": [
                    ("clipless", "Clipless pedals"),
                    ("platform", "Platform pedals"),
                    ("hybrid", "Hybrid pedals")
                ],
                
                "Which stiffness index suits you?": [
                    ("flexible", "5-7 - More flexibility and comfort, ideal for long tours & walking"),
                    ("balanced_stiffness", "8-10 - Perfect balance between comfort & efficiency for training & racing"),
                    ("max_stiffness", "11-15 - Maximum power transfer for competitions & explosive sprints")
                ],
                
                "What fit do you prefer?": [
                    ("tight", "Tight, athletic fit (maximum power transfer)"),
                    ("balanced_fit", "Balanced fit (combination of performance and comfort)"),
                    ("comfortable", "Comfortable fit (more space and comfort for long rides)")
                ],
                
                "Do you want to take your performance to the next level with an individually customized insole?": [
                    ("yes", "Yes, for optimal power transfer and peak performance"),
                    ("no", "No")
                ],
                
                # Soccer Shoes
                "On which surface do you mainly play?": [
                    ("natural_grass", "Natural grass (FG)"),
                    ("artificial_turf", "Artificial turf (AG)"),
                    ("indoor_court", "Indoor court (IC)")
                ],
                
                "What is more important to you - speed or stability?": [
                    ("speed", "Speed - Lightweight shoe for quick starts & direction changes"),
                    ("stability", "Stability - Secure fit & optimal for hard tackles"),
                    ("versatility", "Versatility - Balance of speed & support for flexible playing styles")
                ],
                
                "Which price range do you prefer for your soccer shoes?": [
                    ("entry_level", "Entry-level models (€50 - €100)"),
                    ("mid_range", "Mid-range models (€100 - €200)"),
                    ("premium", "Premium models (over €200)")
                ],
                
                # Climbing Shoes
                "What do you need the climbing shoes for?": [
                    ("multi_pitch", "Multi-pitch climbing / Alpine climbing"),
                    ("bouldering", "Bouldering"),
                    ("sport_climbing", "Sport climbing"),
                    ("crack_climbing", "Crack climbing")
                ],
                
                "What foot shape do you have?": [
                    ("egyptian", "Egyptian"),
                    ("roman", "Roman"),
                    ("greek", "Greek"),
                    ("auto_analysis", "Automatic analysis according to scan")
                ],
                
                "What is most important to you about the sole of your climbing shoe?": [
                    ("feel_precision", "Maximum feel and precision"),
                    ("support_comfort", "Support and comfort"),
                    ("durability", "Durability and robustness"),
                    ("balance_durability", "Balance of durability and performance")
                ],
                
                "Which shape do you prefer?": [
                    ("neutral_shape", "Neutral - Comfortable for long tours & beginners"),
                    ("moderate_curve", "Moderate curvature - Good balance of comfort & precision"),
                    ("aggressive_curve", "Strongly curved (Aggressive) - Maximum precision for overhangs & difficult routes")
                ],
                
                # Tennis Shoes
                "On which surface do you mainly play?": [
                    ("clay", "Clay court"),
                    ("hard", "Hard court"),
                    ("grass", "Grass court"),
                    ("all_court", "All court")
                ],
                
                "Is performance or durability more important to you?": [
                    ("performance", "Maximum performance (Lightweight, agile shoe for quick movements)"),
                    ("durability", "Durability & resilience (More robust materials for longer lifespan)")
                ],
                
                "Do you move more sideways or often sprint forward and backward?": [
                    ("sideways", "Sideways - Frequent lateral movements"),
                    ("forward_back", "Forward & backward - Many quick sprints"),
                    ("both", "Both - A good mix of both")
                ],
                
                # Basketball Shoes
                "What is the surface?": [
                    ("indoor", "Indoor court"),
                    ("outdoor", "Outdoor")
                ],
                
                "Do you need more ankle protection or more freedom of movement?": [
                    ("high_tops", "Maximum protection (High-Tops)"),
                    ("mid_tops", "Balance (Mid-Tops)"),
                    ("low_tops", "Freedom of movement (Low-Tops)")
                ],
                
                # Golf Shoes
                "What is more important to you - stability or comfort?": [
                    ("stability", "Stability - Secure hold & maximum control during the swing"),
                    ("comfort", "Comfort - Longer rounds")
                ],
                
                "Which sole type do you need?": [
                    ("spikeless", "Spikeless"),
                    ("spikes", "Spikes")
                ],
                
                "How important are waterproofing and breathability for your golf shoes?": [
                    ("max_waterproof", "Maximum waterproofing, less breathability"),
                    ("balanced_wb", "Good balance between waterproof & breathable"),
                    ("max_breathability", "No waterproofing needed, maximum ventilation")
                ],
                
                # Hiking Shoes
                "How do you prefer your hiking boots to fit?": [
                    ("normal_fit", "Normal fit - Ideal for everyday wear and lighter tours"),
                    ("roomy_fit", "Slightly roomier - for mountain hiking or if you consciously want more space, e.g., for thick socks")
                ],
                
                "On which surface will you mainly use the shoe?": [
                    ("everyday", "Everyday use & light paths - city or simple walks"),
                    ("normal_tours", "Normal mountain tours - forest and mountain paths, also uneven"),
                    ("high_altitude", "High-altitude tours & alpine terrain - rocky, steep, or high alpine")
                ],
                
                "Which shaft height do you prefer?": [
                    ("high_cut", "High-Cut - Maximum support and ankle protection for difficult terrain"),
                    ("mid_cut", "Mid-Cut - Good balance of mobility and support for versatile tours"),
                    ("low_cut", "Low-Cut - Lightweight and flexible for fast, easy paths")
                ],
                
                "Should the shoe be waterproof?": [
                    ("not_decisive", "Not a decisive factor"),
                    ("breathable", "Breathable, non-waterproof shoes"),
                    ("waterproof_membrane", "Waterproof membrane (e.g., Gore-Tex®)")
                ],
                
                # Everyday Shoes
                "Which everyday shoes are you looking for?": [
                    ("sneakers", "Sneakers"),
                    ("sandals", "Sandals"),
                    ("dress_shoes", "Dress shoes"),
                    ("work_shoes", "Work shoes"),
                    ("sports_shoes", "Sports shoes"),
                    ("comfort_shoes", "Comfort shoes")
                ],
                
                "Do you own orthopedic insoles?": [
                    ("yes_insoles", "Yes"),
                    ("no_insoles", "No"),
                    ("planned_insoles", "Planned")
                ]
            }

        try:
            for q_label, ans_list in QUESTION_ANSWERS_MAP.items():
                question_obj, created = ShoesQuestion.objects.get_or_create(
                    key=q_label.lower().replace(" ", "_")[:255],
                    defaults={"label": q_label}
                )
                for ans_key, ans_label in ans_list:
                    ShoesAnswer.objects.get_or_create(
                        question=question_obj,
                        key=ans_key,
                        defaults={"label": ans_label}
                    )
        except OperationalError:
            # Database not ready yet (migrations not applied)
            pass
