from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError

class OthersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Others'

    def ready(self):
        
        from .models import Question, Answer
        def populate_questions(sender, **kwargs):
            
            QUESTION_ANSWERS_MAP = {
                    "For what purpose are you looking for running shoes?": [
                        ("allrounder", "All-rounder"),
                        ("trail_running", "Trail running (terrain)"),
                        ("long_distance", "Long distances/endurance"),
                        ("race_marathon", "Competition/Marathon"),
                        ("interval_training", "Interval running/runs"),
                        ("walking", "Walking shoes")
                    ],
                
                    "How do you prefer your shoes to fit?": [
                        ("perfect_fit_running", "The perfect running shoe fit based on my 3D scan"),
                        ("roomy_running", "Rather roomier, as I prefer more freedom of movement"),
                        ("snug_running", "Rather tighter, as I like my shoes to fit snugly on my foot")
                    ],
                
                    "On which surface will you primarily be moving?": [
                        ("hard_surface", "Hard surface - asphalt, cobblestones, sidewalks"),
                        ("mixed_terrain", "Mixed terrain - a mix of natural and urban paths")
                    ],
                
                    "Do you prefer a higher sole or a normal to mid-height sole?": [
                        ("higher_sole", "Higher sole - focus on comfort"),
                        ("normal_mid_sole", "Normal to mid-height sole - focus on natural rolling movement")
                    ],
                
                    "On which surface do you run your interval training?": [
                        ("track_spikes", "Running track (spikes)"),
                        ("asphalt_track", "Asphalt/running track (without spikes)")
                    ],
                
                    "What distance do you run in your interval training?": [
                        ("short_distance", "Short distance (100-400 m)"),
                        ("middle_long_distance", "Middle & long distance (800 m - 10000 m)")
                    ],
                                                    
                    "On which surface will you primarily be running?": [
                        ("asphalt_road", "Asphalt/Road - For regular, firm surfaces"),
                        ("mixed", "Mixed - For varying surfaces")
                    ],
                
                    "Have you ever had problems or pain while running?": [
                        ("no_problems", "No"),
                        ("knee_problems", "Yes, knee problems"),
                        ("calf_problems", "Yes, calf problems"),
                        ("shin_splints", "Yes, shin splints"),
                        ("plantar_fasciitis", "Yes, plantar fasciitis (heel pain)")
                    ],
                
                    "Do you know your foot type or pronation?": [
                        ("scan_analysis", "Analysis based on my 3D scan"),
                        ("neutral", "Neutral foot"),
                        ("overpronation", "Overpronation (excessive inward roll)")
                    ],
                
                    "What role does cushioning play in relation to stability?": [
                        ("max_cushioning", "Maximum cushioning - focus on comfort and joint protection"),
                        ("balanced", "Balanced - good ratio of cushioning and stability"),
                        ("more_stability", "More stability - focus on control and guidance")
                    ],
                
                    "How do you prefer your all-round running shoes to fit?": [
                        ("perfect_fit_all-round", "The perfect running shoe fit based on my 3D scan"),
                        ("roomy_all-round", "Rather roomier, as I prefer more freedom of movement"),
                        ("snug_all-round", "Rather tighter, as I like my shoes to fit snugly on my foot")
                    ],
                
                    "Should your shoe be waterproof (Gore-Tex membrane)?": [
                        ("yes_waterproof", "Yes, waterproof and breathable (Gore-Tex or similar membrane)"),
                        ("no_waterproof", "No, lighter and better ventilated")
                    ],
                
                    "Where will you primarily use your trail running shoes?": [
                        ("trails_only", "Only on trails & off-road"),
                        ("hybrid_use", "Mix of trail & road (hybrid use)")
                    ],
                
                    "What shaft height should your shoe have?": [
                        ("low", "Low (below the ankle)"),
                        ("mid_high", "Mid/High (ankle height or above)")
                    ],
                
                    "How do you prefer your competition shoes to fit?": [
                        ("perfect_fit_competition", "The perfect competition fit based on my 3D scan"),
                        ("roomy_competition", "Rather roomier, as I prefer more freedom of movement"),
                        ("snug_competition", "Rather tighter, as I like my shoes to fit snugly on my foot")
                    ],
                
                    "What type of competition shoes are you looking for?": [
                        ("with_carbon", "Competition shoes with carbon"),
                        ("without_carbon", "Competition shoes without carbon")
                    ],
                
                    "For which distance are you looking for competition shoes?": [
                        ("short_race", "Short distance (5 km - 10 km)"),
                        ("half_marathon", "Half marathon (21.1 km)"),
                        ("marathon", "Marathon (42.2 km & more)")
                    ],
                
                    "What heel-to-toe drop do you prefer?": [
                        ("standard_drop", "6-10 mm - Proven choice, supports the rolling motion"),
                        ("minimal_drop", "≤ 6 mm - Direct ground feel, requires trained technique")
                    ],
                            
                    "Which fit do you prefer?": [
                        ("tight", "Tight, performance fit (maximum power transfer)"),
                        ("balanced_fit", "Balanced fit (combination of performance and comfort)"),
                        ("comfortable", "Comfort fit (more space and comfort for long rides)")
                    ],
                
                    "What type of cycling do you do?": [
                        ("road_bike", "Road Bike"),
                        ("mountain_bike", "Mountain Bike"),
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
                
                    "Would you like to take your performance to the next level with a custom-fit insole?": [
                        ("yes", "Yes, for optimal power transfer and peak performance"),
                        ("no", "No")
                    ],

                    "How do you prefer your football shoes to fit?": [
                        ("perfect_fit_football", "The perfect football boot fit based on my 3D scan"),
                        ("roomy_football", "Rather roomier, as I prefer more freedom of movement")
                    ],
                
                    "On which surface do you mainly play football?": [
                        ("natural_grass", "Natural grass (FG)"),
                        ("artificial_turf", "Artificial turf (AG)"),
                        ("indoor_court", "Indoor court (IC)")
                    ],
                
                    "What is more important to you - speed or stability?": [
                        ("speed", "Speed - Lightweight shoe for quick starts & direction changes"),
                        ("stability", "Stability - Secure fit & optimal for tough tackles"),
                        ("versatility", "Versatility - Balance of speed & support for flexible playing styles")
                    ],
                
                    "Which price range do you prefer for your football boots?": [
                        ("entry_level", "Entry-level models (€50 - €100)"),
                        ("mid_range", "Mid-range models (€100 - €200)"),
                        ("premium", "Premium models (over €200)")
                    ],

                    "How do you prefer your climbing shoes to fit?": [
                        ("perfect_fit_climbing", "The recommended climbing shoe fit based on my 3D scan"),
                        ("roomy_climbing", "Rather roomier for more freedom of movement and higher wearing comfort")
                    ],
                
                    "What do you need the climbing shoes for?": [
                        ("multi_pitch", "Multi-pitch / Alpine climbing"),
                        ("bouldering", "Bouldering"),
                        ("sport_climbing", "Sport climbing"),
                        ("crack_climbing", "Crack climbing")
                    ],
                
                    "What is your foot shape?": [
                        ("egyptian", "Egyptian"),
                        ("roman", "Roman"),
                        ("greek", "Greek"),
                        ("auto_analysis", "Automatic analysis according to scan")
                    ],
                
                    "What is most important to you in the sole of your climbing shoe?": [
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

                    "How do you prefer your tennis shoes to fit?": [
                        ("perfect_fit_tennis", "The perfect tennis shoe fit based on my 3D scan"),
                        ("snug_tennis", "Rather tighter, as I like my shoes to fit snugly on my foot"),
                        ("roomy_tennis", "Rather roomier, as I prefer more freedom of movement")
                    ],

                    "Is performance or durability more important to you?": [
                        ("performance", "Maximum performance (Lighter, more agile shoe for quick movements)"),
                        ("durability", "Durability & resilience (More robust materials for longer lifespan)")
                    ],
                
                    "Do you move more sideways or often sprint forward and backward?": [
                        ("sideways", "Sideways - Frequent lateral movements"),
                        ("forward_back", "Forward & Backward - Lots of quick sprints"),
                        ("both", "Both - A good mix of both")
                    ],

                    "How do you prefer your basketball shoes to fit?": [
                        ("perfect_fit_basketball", "The perfect basketball shoe fit based on my 3D scan"),
                        ("snug_basketball", "Rather tighter, as I like my shoes to fit snugly on my foot"),
                        ("roomy_basketball", "Rather roomier, as I prefer more freedom of movement")
                    ],
                
                    "Traction & Grip - What is the surface?": [
                        ("indoor", "Indoor court"),
                        ("outdoor", "Outdoor")
                    ],
                
                    "Do you need more ankle protection or more freedom of movement?": [
                        ("high_tops", "Lots of protection (High-Tops)"),
                        ("mid_tops", "Balance (Mid-Tops)"),
                        ("low_tops", "Freedom of movement (Low-Tops)")
                    ],
                        
                    "How do you prefer your golf shoes to fit?": [
                        ("perfect_fit_golf", "The perfect recommended golf shoe fit based on my 3D scan"),
                        ("snug_golf", "Rather tighter, as I like my shoes to fit snugly on my foot"),
                        ("roomy_golf", "Rather roomier, as I prefer more freedom of movement")
                    ],
                
                    "Spikes or Spikeless - Which sole type do you need?": [
                        ("spikeless", "Spikeless"),
                        ("spikes", "Spikes")
                    ],
                
                    "How important are waterproofing and breathability for your golf shoes?": [
                        ("max_waterproof", "Maximum waterproofing, less breathability"),
                        ("balanced_wb", "Good balance between waterproof & breathable"),
                        ("max_breathability", "No waterproofing necessary, maximum ventilation")
                    ],
                
                    "What is more important to you - stability or comfort?": [
                        ("stability", "Stability - Secure hold & maximum control during the swing"),
                        ("comfort", "Comfort - Longer rounds")
                    ],

                    "How do you prefer your hiking boots to fit?": [
                        ("normal_fit", "Normal fit - Ideal for day and lighter tours"),
                        ("roomy_fit", "A bit roomier - for mountain tours in the high mountains or if you consciously want more space, e.g., for thick socks")
                    ],
                
                    "On which surface will you mainly use the shoe?": [
                        ("everyday", "Everyday & Light Trails - City or Easy Walks"),
                        ("normal_tours", "Normal Mountain Tours - Forest and Mountain Paths, Also Uneven"),
                        ("high_altitude", "High Altitude & Alpine Terrain – Rocky, Steep, or High Alpine")
                    ],
                
                    "Which shaft height do you prefer?": [
                        ("high_cut", "High-Cut - Maximum support and ankle protection for difficult terrain"),
                        ("mid_cut", "Mid-Cut - Good balance of mobility and support for versatile tours"),
                        ("low_cut", "Low-Cut - Light and flexible for fast, easy trails")
                    ],
                
                    "Should the shoe be waterproof?": [
                        ("not_decisive", "Not a decisive factor"),
                        ("breathable", "Breathable, non-waterproof shoes"),
                        ("waterproof_membrane", "Waterproof membrane (e.g., Gore-Tex®)")
                    ],
                        
                    "Which everyday shoes are you looking for?": [
                        ("sneakers", "Sneakers"),
                        ("sandals", "Sandals"),
                        ("dress_shoes", "Dress Shoes"),
                        ("work_shoes", "Work Shoes"),
                        ("sports_shoes", "Athletic Shoes"),
                        ("comfort_shoes", "Comfort Shoes")
                    ],
                
                    "How do you prefer your sneaker shoes to fit?": [
                        ("perfect_fit_sneaker", "The perfect recommended fit based on my 3D scan"),
                        ("snug_sneaker", "Rather tighter, as I like my shoes to fit snugly on my foot"),
                        ("roomy_sneaker", "Rather roomier, as I prefer more freedom of movement")
                    ],
                
                    "Do you own orthopedic insoles?": [
                        ("yes_insoles", "Yes"),
                        ("no_insoles", "No"),
                        ("planned_insoles", "In planning")
                    ],

                    "How do you prefer your comfortable shoes to fit?": [
                        ("perfect_fit_comfortable", "The perfect recommended fit based on my 3D scan"),
                        ("snug_comfortable", "Rather tighter, as I like my shoes to fit snugly on my foot"),
                        ("roomy_comfortable", "Rather roomier, as I prefer more freedom of movement")
                    ],

                    "How do you prefer your sandals shoes to fit?": [
                        ("perfect_fit_sandals", "The perfect recommended fit based on my 3D scan"),
                        ("snug_sandals", "Rather tighter, as I like my shoes to fit snugly on my foot"),
                        ("roomy_sandals", "Rather roomier, as I prefer more freedom of movement")
                    ],
                
                    "How do you prefer your work shoes to fit?": [
                        ("perfect_fit_work", "The perfect recommended fit based on my 3D scan"),
                        ("snug_work", "Rather tighter, as I like my shoes to fit snugly on my foot"),
                        ("roomy_work", "Rather roomier, as I prefer more freedom of movement")
                    ],

                    "How do you prefer your hockey shoes to fit?": [
                        ("perfect_fit_hockey", "The perfect recommended fit based on my 3D scan"),
                        ("snug_hockey", "Rather tighter, as I like my shoes to fit snugly on my foot"),
                        ("roomy_hockey", "Rather roomier, as I prefer more freedom of movement")
                    ],
                        
                    "How do you prefer your boots to fit?": [
                        ("perfect_fit_ski", "The perfect recommended fit based on my 3D scan"),
                        ("snug_ski", "Rather tighter, as I like my boots to fit snugly on my foot"),
                        ("roomy_ski", "Rather roomier, as I prefer more freedom of movement")
                    ],
                        
                    "How do you prefer your elegant shoes to fit?": [
                        ("perfect_fit_elegant", "The perfect recommended fit based on my 3D scan"),
                        ("snug_elegant", "Rather tighter, as I like my shoes to fit snugly on my foot"),
                        ("roomy_elegant", "Rather roomier, as I prefer more freedom of movement")
                    ],
                
                    "How do you prefer your miscellaneous shoes to fit?": [
                        ("perfect_fit_miscellaneous", "The perfect recommended fit based on my 3D scan"),
                        ("snug_miscellaneous", "Rather tighter, as I like my shoes to fit snugly on my foot"),
                        ("roomy_miscellaneous", "Rather roomier, as I prefer more freedom of movement")
                    ],
                }; 
            try:
                for q_label, ans_list in QUESTION_ANSWERS_MAP.items():
                    question_key = q_label.lower().replace(' ', '_')[:240]
                    question_obj, created = Question.objects.get_or_create(
                        key=question_key,
                        defaults={"label": q_label}
                    )
                    for ans_key, ans_label in ans_list:
                        Answer.objects.get_or_create(
                            question=question_obj,
                            key=ans_key,
                            defaults={"label": ans_label}
                        )
            except OperationalError:
                pass
        post_migrate.connect(populate_questions, sender=self)