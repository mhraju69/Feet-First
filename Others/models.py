from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage
from Products.models import *
from itertools import chain

# Create your models here.
class ShoesQuestion(models.TextChoices):
    # General / reusable
    FIT_PREFERENCE = "fit_preference", "How do you prefer your shoes to fit?"
    SHAFT_HEIGHT = "shaft_height", "Which shaft height do you prefer?"
    WATERPROOF = "waterproof", "Should the shoe be waterproof?"
    PLAYING_SURFACE = "playing_surface", "On which surface do you mainly play?"

    # Running
    PURPOSE = "purpose", "What purpose are you looking for running shoes for?"
    SURFACE = "surface", "On which surface will you mainly be running?"
    FOOT_TYPE = "foot_type", "Do you know your foot type or pronation?"
    RUNNING_PROBLEMS = "running_problems", "Have you ever had any problems or pain while running?"
    CUSHIONING_STABILITY = "cushioning_stability", "What role does cushioning play in relation to stability?"
    SOLE_HEIGHT = "sole_height", "Do you prefer a higher sole or a normal to mid-range sole height?"

    # Trail Running
    TRAIL_USAGE = "trail_usage", "How will you primarily use your trail running shoes?"

    # Interval Training
    INTERVAL_SURFACE = "interval_surface", "On which surface do you run your interval training?"
    INTERVAL_DISTANCE = "interval_distance", "Which distance do you run in your interval training?"

    # Racing
    RACING_TYPE = "racing_type", "What type of racing shoes are you looking for?"
    RACING_DISTANCE = "racing_distance", "For which distance are you looking for racing shoes?"
    DROP_PREFERENCE = "drop_preference", "What drop do you prefer?"
    CYCLING_TYPE = "cycling_type", "What type of cycling do you do?"
    PEDAL_TYPE = "pedal_type", "What type of pedals do you use?"
    STIFFNESS_INDEX = "stiffness_index", "Which stiffness index suits you?"
    CUSTOM_INSOLE = "custom_insole", "Do you want to take your performance to the next level with an individually customized insole?"

    # Soccer
    PRIORITY = "priority", "What is more important to you - speed or stability?"
    PRICE_RANGE = "price_range", "Which price range do you prefer for your soccer shoes?"
    ANKLE_SUPPORT = "ankle_support", "Do you need more ankle protection or more freedom of movement?"

    # Climbing
    CLIMBING_PURPOSE = "climbing_purpose", "What do you need the climbing shoes for?"
    FOOT_SHAPE = "foot_shape", "What foot shape do you have?"
    SOLE_PRIORITY = "sole_priority", "What is most important to you about the sole of your climbing shoe?"
    SHAPE_PREFERENCE = "shape_preference", "Which shape do you prefer?"

    # Court Sports
    COURT_SURFACE = "court_surface", "On which surface do you mainly play?"
    PERFORMANCE_DURABILITY = "performance_durability", "Is performance or durability more important to you?"
    MOVEMENT_TYPE = "movement_type", "Do you move more sideways or often sprint forward and backward?"

    # Golf
    STABILITY_COMFORT = "stability_comfort", "What is more important to you - stability or comfort?"
    SOLE_TYPE = "sole_type", "Which sole type do you need?"
    WATERPROOF_BREATHABILITY = "waterproof_breathability", "How important are waterproofing and breathability for your golf shoes?"

    # Hiking
    TERRAIN = "terrain", "On which surface will you mainly use the shoe?"

    # Everyday
    SHOE_TYPE = "shoe_type", "Which everyday shoes are you looking for?"
    ORTHOPEDIC_INSOLES = "orthopedic_insoles", "Do you own orthopedic insoles?"

class ShoesAnswer(models.TextChoices):
    # General / reusable
    PERFECT_FIT = "perfect_fit", "Perfect fit based on 3D scan"
    SNUG = "snug", "Rather snug, as I like my shoes to fit tightly"
    ROOMY = "roomy", "Rather roomy, for more freedom of movement"
    NORMAL_FIT = "normal_fit", "Normal fit - ideal for everyday use"
    NEUTRAL = "neutral", "Neutral - Comfortable for long tours & beginners"
    
    YES = "yes", "Yes"
    NO = "no", "No"
    
    WATERPROOF = "waterproof", "Should the shoe be waterproof?"
    SHAFT_HEIGHT = "shaft_height", "Which shaft height do you prefer?"
    PLAYING_SURFACE = "playing_surface", "On which surface do you mainly play?"
    SHOE_TYPE = "shoe_type", "Which everyday shoes are you looking for?"
    
    # Running types
    ALLROUNDER = "allrounder", "All-rounder"
    RACE_MARATHON = "race_marathon", "Race/Marathon"
    TRAIL_RUNNING = "trail_running", "Trail running (off-road)"
    INTERVAL_TRAINING = "interval_training", "Interval runs/Track workouts"
    LONG_DISTANCE = "long_distance", "Long distances/Long runs"
    WALKING = "walking", "Walking shoes"

    # Cushioning & stability
    MAX_CUSHIONING = "max_cushioning", "Maximum cushioning - focus on comfort"
    BALANCED = "balanced", "Balanced - good ratio of cushioning & stability"
    MORE_STABILITY = "more_stability", "More stability - focus on control"

    # Sole height
    HIGHER_SOLE = "higher_sole", "Higher sole - focus on comfort"
    NORMAL_MID_SOLE = "normal_mid_sole", "Normal to mid-range sole - natural rolling"

    # Trail usage
    TRAILS_ONLY = "trails_only", "Only on trails & off-road"
    HYBRID_USE = "hybrid_use", "Mix of trail & road (hybrid use)"

    # Waterproof
    YES_WATERPROOF = "yes_waterproof", "Yes, waterproof and breathable"
    NO_WATERPROOF = "no_waterproof", "No, lighter and ventilated"

    # Shaft height
    LOW = "low", "Low (below the ankle)"
    MID_HIGH = "mid_high", "Mid/High (ankle-high or above)"

    # Interval distances
    SHORT_DISTANCE = "short_distance", "Short distance (100-400 m)"
    MIDDLE_LONG_DISTANCE = "middle_long_distance", "Middle & long distance (800 m - 10,000 m)"

    # Racing
    WITH_CARBON = "with_carbon", "Racing shoes with carbon"
    WITHOUT_CARBON = "without_carbon", "Racing shoes without carbon"

    SHORT_RACE = "short_race", "Short distance (5-10 km)"
    HALF_MARATHON = "half_marathon", "Half marathon (21.1 km)"
    MARATHON = "marathon", "Marathon (42.2 km & more)"

    STANDARD_DROP = "standard_drop", "6-10 mm - proven choice"
    MINIMAL_DROP = "minimal_drop", "≤ 6 mm - direct push-off"

    # Cycling
    ROAD_BIKE = "road_bike", "Road bike"
    MOUNTAIN_BIKE = "mountain_bike", "Mountain bike"
    GRAVEL = "gravel", "Gravel"
    CLIPLESS = "clipless", "Clipless pedals"
    PLATFORM = "platform", "Platform pedals"
    HYBRID = "hybrid", "Hybrid pedals"
    FLEXIBLE = "flexible", "5-7 - more flexibility, comfort"
    BALANCED_STIFFNESS = "balanced_stiffness", "8-10 - balance of comfort & efficiency"
    MAX_STIFFNESS = "max_stiffness", "11-15 - maximum power transfer"

    TIGHT = "tight", "Tight, athletic fit"
    BALANCED_FIT = "balanced_fit", "Balanced fit (performance & comfort)"
    COMFORTABLE = "comfortable", "Comfortable fit (more space)"

    CUSTOM_INSOLE = "custom_insole", "Individually customized insole"

    # Soccer
    PRIORITY = "priority", "What is more important - speed or stability?"
    PRICE_RANGE = "price_range", "Preferred price range"
    NATURAL_GRASS = "natural_grass", "Natural grass (FG)"
    ARTIFICIAL_TURF = "artificial_turf", "Artificial turf (AG)"
    INDOOR_COURT = "indoor_court", "Indoor court (IC)"
    SPEED = "speed", "Speed - lightweight, quick starts"
    STABILITY = "stability", "Stability - secure fit, optimal control"
    VERSATILITY = "versatility", "Versatility - balance of speed & support"
    ENTRY_LEVEL = "entry_level", "Entry-level (€50-100)"
    MID_RANGE = "mid_range", "Mid-range (€100-200)"
    PREMIUM = "premium", "Premium (> €200)"
    ANKLE_SUPPORT = "ankle_support", "More ankle protection or freedom of movement"

    # Climbing
    CLIMBING_PURPOSE = "climbing_purpose", "Purpose of climbing shoes"
    FOOT_SHAPE = "foot_shape", "Foot shape"
    SOLE_PRIORITY = "sole_priority", "Important sole feature"
    SHAPE_PREFERENCE = "shape_preference", "Preferred shape"
    MULTI_PITCH = "multi_pitch", "Multi-pitch/alpine"
    BOULDERING = "bouldering", "Bouldering"
    SPORT_CLIMBING = "sport_climbing", "Sport climbing"
    CRACK_CLIMBING = "crack_climbing", "Crack climbing"
    EGYPTIAN = "egyptian", "Egyptian"
    ROMAN = "roman", "Roman"
    GREEK = "greek", "Greek"
    AUTO_ANALYSIS = "auto_analysis", "Automatic scan analysis"
    FEEL_PRECISION = "feel_precision", "Maximum feel and precision"
    SUPPORT_COMFORT = "support_comfort", "Support and comfort"
    DURABILITY = "durability", "Durability & robustness"
    BALANCE_DURABILITY = "balance_durability", "Balance of durability and performance"
    MODERATE_CURVE = "moderate_curve", "Moderate curvature - comfort & precision"
    AGGRESSIVE_CURVE = "aggressive_curve", "Strongly curved - maximum precision"

    # Court sports / Tennis
    COURT_SURFACE = "court_surface", "On which surface do you mainly play?"
    PERFORMANCE_DURABILITY = "performance_durability", "Performance or durability?"
    MOVEMENT_TYPE = "movement_type", "Sideways or forward/backward movements?"
    CLAY = "clay", "Clay court"
    HARD = "hard", "Hard court"
    GRASS = "grass", "Grass court"
    ALL_COURT = "all_court", "All court"
    PERFORMANCE = "performance", "Maximum performance"
    COMFORT = "comfort", "Comfortable play"
    SPIKELESS = "spikeless", "Spikeless"
    SPIKES = "spikes", "Spikes"
    MAX_WATERPROOF = "max_waterproof", "Maximum waterproofing"
    BALANCED_WB = "balanced_wb", "Balanced waterproof & breathable"
    MAX_BREATHABILITY = "max_breathability", "Maximum ventilation"

    # Hiking / Outdoors
    TERRAIN = "terrain", "Surface you will mainly use the shoe on"
    NORMAL_TOURS = "normal_tours", "Normal mountain tours"
    HIGH_ALTITUDE = "high_altitude", "High-altitude tours"
    HIGH_CUT = "high_cut", "High-Cut support"
    MID_CUT = "mid_cut", "Mid-Cut balance"
    LOW_CUT = "low_cut", "Low-Cut, lightweight"
    BREATHABLE = "breathable", "Breathable, non-waterproof"
    WATERPROOF_MEMBRANE = "waterproof_membrane", "Waterproof membrane (e.g., Gore-Tex®)"

    # Everyday shoes
    SNEAKERS = "sneakers", "Sneakers"
    SANDALS = "sandals", "Sandals"
    DRESS_SHOES = "dress_shoes", "Dress shoes"
    WORK_SHOES = "work_shoes", "Work shoes"
    SPORTS_SHOES = "sports_shoes", "Sports shoes"
    COMFORT_SHOES = "comfort_shoes", "Comfort shoes"

    # Insoles
    YES_INSOLES = "yes_insoles", "Yes"
    NO_INSOLES = "no_insoles", "No"
    PLANNED_INSOLES = "planned_insoles", "Planned"

class FAQ(models.Model):
    question_de = models.CharField(max_length=200 , verbose_name ="Question (German)")
    question_it = models.CharField(max_length=200 , verbose_name="Question (Italian)")
    answer_de = models.TextField(verbose_name ="Answer (German)")
    answer_it = models.TextField(verbose_name="Answer (Italian)")

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return f"FAQ for: {self.question_de}"

class News(models.Model):
    title_de = models.CharField(max_length=200 , verbose_name ="Title (German)")
    title_it = models.CharField(max_length=200 , verbose_name="Title (Italian)")
    image = models.ImageField(upload_to='news_images/',storage=MediaCloudinaryStorage())
    content_de = models.TextField(verbose_name ="Content (German)")
    content_it = models.TextField(verbose_name="Content (Italian)")
    created_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'

    def __str__(self):
        return f"{self.title_de} - {self.title_it}"


class Question(models.Model):
    sub_category = models.CharField(max_length=100,choices=SubCategory.choices ,blank=True, null=True)
    key = models.CharField(max_length=255, unique=True)
    label = models.TextField()

    def __str__(self):
        return self.label


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    key = models.CharField(max_length=255)
    label = models.TextField()

    def __str__(self):
        return f"{self.label}"
    
    @property
    def sub_category(self):
        return self.product.sub_category if self.product else None

    class Meta:
        verbose_name = 'Question & Answer'

class ProductQuestionAnswer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="question_answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="product_questions")
    answers = models.ManyToManyField(Answer,related_name="product_answers")

    def __str__(self):
        return f"{self.product.name} - {self.question.label}"
    class Meta:
        verbose_name = 'Question & Answer'