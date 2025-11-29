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
                # ============ CYCLING SHOES ============
                ("Cycling Shoes: Welche Passform bevorzugst du?", "cycling-shoes_welche_passform_bevorzugst_du?"): [
                        "Enge, sportliche Passform (maximale Kraftübertragung)",
                        "Ausgewogene Passform (Kombination aus Performance und Komfort)",
                        "Bequeme Passform (mehr Platz und Komfort für Lange Fahrten)"
                    ],
                ("Cycling Shoes: Welche Art von Radsport betreibst du?", "cycling-shoes_welche_art_von_radsport_betreibst_du?"): [
                        "Rennrad",
                        "Mountainbike",
                        "Gravel"
                    ],
                ("Cycling Shoes: Welche Art von Pedalen benutzt du?", "cycling-shoes_welche_art_von_pedalen_benutzt_du?"): [
                        "Klickpedale",
                        "Plattformpedale",
                        "Hybridpedale"
                    ],
                ("Cycling Shoes: Welcher Steifigkeitsindex passt zu dir?", "cycling-shoes_welcher_steifigkeitsindex_passt_zu_dir?"): [
                        "5–7 – Mehr Flexibilität und Komfort, ideal für lange Touren & Gehen.",
                        "8–10 – Perfekte Balance zwischen Komfort & Effizienz für Training & Rennen.",
                        "11–15 – Maximale Kraftübertragung für Wettkämpfe & explosive Sprints."
                    ],
                ("Cycling Shoes: Möchtest du mit einer individuell angepassten Winsole deine Performance auf das nächste Level heben?", "cycling-shoes_möchtest_du_mit_einer_individuell_angepassten_winsole_deine_performance_auf_das_nächste_level_heben?"): [
                        "Ja, für optimale Kraftübertragung und Bestleistung",
                        "Nein"
                    ],
                
                # ============ CASUAL SHOES ============
                ("Casual Shoes: Welche Alltagsschuhe suchen sie?", "casual-sneaker_welche_alltagsschuhe_suchen_sie"): [
                        "Sneaker",
                        "Anzugsschuhe",
                        "Sportschuhe",
                        "Sandalen",
                        "Arbeitsschuhe",
                        "Bequemschuhe"
                    ],
                ("Casual Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "casual-sneaker_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                        "Die perfekt empfohlene Passform basierend auf meinem 3D-Scan",
                        "Eher enger, da ich meine Schuhe gern fest am Fuß trage",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge"
                    ],
                ("Casual Shoes: Sind Sie im Besitz einer Orthopädischen Einlage?", "casual-sneaker_sind_sie_im_besitz_einer_orthopädischen_einlage"): [
                        "Ja",
                        "Nein",
                        "in Planung"
                    ],
                
                # ============ MOUNTAIN/TREKKING SHOES ============
                ("Mountain/Trekking Shoes: Wie bevorzugen Sie Ihre Bergschuhe zu tragen?", "mountain-trekking-shoes_wie_bevorzugen_sie_ihre_bergschuhe_zu_tragen"): [
                        "Normale Passform – Ideal für Alltag und leichtere Touren.",
                        "Etwas weiter – für Bergtouren im Gebirge oder wenn du bewusst mehr Platz, z. B. für dicke Socken, wünschst."
                    ],
                ("Mountain/Trekking Shoes: Auf welchem Untergrund werden Sie den Schuh hauptsächlich nutzen?", "mountain-trekking-shoes_auf_welchem_untergrund_werden_sie_den_schuh_hauptsächlich_nutzen"): [
                        "Alltag & leichte Wege – Stadt oder einfache Spaziergänge",
                        "Normale Bergtouren – Wald- und Bergwege, auch uneben",
                        "Hochtouren & alpines Gelände – felsig, steil oder hochalpin"
                    ],
                ("Mountain/Trekking Shoes: Welche Schafthöhe bevorzugen Sie?", "mountain-trekking-shoes_welche_schafthöhe_bevorzugen_sie"): [
                        "High-Cut – Maximaler Halt und Knöchelschutz für schwieriges Gelände.",
                        "Mid-Cut – Gute Balance aus Beweglichkeit und Halt für vielseitige Touren.",
                        "Low-Cut – Leicht und flexibel für schnelle, einfache Wege."
                    ],
                ("Mountain/Trekking Shoes: Soll der Schuh wasserdicht sein?", "mountain-trekking-shoes_soll_der_schuh_wasserdicht_sein"): [
                        "Spielt keine entscheidende Rolle",
                        "Atmungsaktive, nicht wasserdichte Schuhe",
                        "Wasserdichte Membran (z. B. Gore-Tex®)"
                    ],
                
                # ============ GOLF SHOES ============
                ("Golf Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "golf-shoes_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                        "Die perfekt empfohlene Golfschuh-Passform basierend auf meinem 3D-Scan",
                        "Eher enger, da ich meine Schuhe gern fest am Fuß trage",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge"
                    ],
                ("Golf Shoes: Spikes oder Spikeless – Welcher Sohlen-Typ benötigst du?", "golf-shoes_spikes_oder_spikeless_welcher_sohlen-typ_benötigst_du"): [
                        "Spikeless",
                        "Spikes"
                    ],
                ("Golf Shoes: Wie wichtig sind Wasserdichtigkeit und Atmungsaktivität bei deinen Golfschuhen?", "golf-shoes_wie_wichtig_sind_wasserdichtigkeit_und_atmungsaktivität_bei_deinen_golfschuhen"): [
                        "Maximale Wasserdichtigkeit, weniger Atmungsaktivität",
                        "Gute Balance zwischen wasserdicht & atmungsaktiv",
                        "Keine Wasserdichtigkeit nötig, maximale Belüftung"
                    ],
                ("Golf Shoes: Was ist dir wichtiger – Stabilität oder Komfort?", "golf-shoes_was_ist_dir_wichtiger_stabilität_oder_komfort"): [
                        "Stabilität – Sicherer Halt & maximale Kontrolle beim Schwung",
                        "Komfort – Längere Runden"
                    ],
                
                # ============ BASKETBALL SHOES ============
                ("Basketball Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "basketball-shoes_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                        "Die perfekte Baskettball-schuhpassform basierend auf meinen 3D-Scan",
                        "Eher enger, da ich meine Schuhe gern fest am Fuß trage",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge"
                    ],
                ("Basketball Shoes: Traktion & Grip – Wie ist der Untergrund?", "basketball-shoes_traktion_&_grip_wie_ist_der_untergrund"): [
                        "Indoor-Halle",
                        "Outdoor"
                    ],
                ("Basketball Shoes: Brauchst du mehr Knöchelschutz oder mehr Bewegungsfreiheit?", "basketball-shoes_brauchst_du_mehr_knöchelschutz_oder_mehr_bewegungsfreiheit"): [
                        "Viel Schutz (High-Tops)",
                        "Balance (Mid-Tops)",
                        "Bewegungsfreiheit (Low-Tops)"
                    ],
                
                # ============ TENNIS SHOES ============
                ("Tennis Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "tennis-shoes_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                        "Die perfekte Tennisschuh-passform basierend auf meinen 3D-Scan",
                        "Eher enger, da ich meine Schuhe gern fest am Fuß trage",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge"
                    ],
                ("Tennis Shoes: Auf welchem Belag spielen Sie hauptsächlich?", "tennis-shoes_auf_welchem_belag_spielen_sie_hauptsächlich"): [
                        "Sandplatz/Claycourt",
                        "Hartplatz/Allcourt",
                        "Rasenplatz"
                    ],
                ("Tennis Shoes: Ist dir Performance oder Langlebigkeit wichtiger?", "tennis-shoes_ist_dir_performance_oder_langlebigkeit_wichtiger"): [
                        "Maximale Performance (Leichter, agiler Schuh für schnelle Bewegungen)",
                        "Langlebigkeit & Strapazierfähigkeit (Robustere Materialien für längere Haltbarkeit)"
                    ],
                ("Tennis Shoes: Wie bewegst du dich auf dem Platz am meisten?", "tennis-shoes_wie_bewegst_du_dich_auf_dem_platz_am_meisten"): [
                        "Seitlich – Häufige Seitwärtsbewegungen",
                        "Vor & zurück – Viele schnelle Sprints",
                        "Beides – Ein guter Mix aus beiden"
                    ],
                
                # ============ SKI BOOTS ============
                ("Ski Boots: Sind Sie Anfänger, Fortgeschrittener oder Experte?", "ski-boots_sind_sie_anfänger_fortgeschrittener_oder_experte"): [
                        "Anfänger",
                        "Fortgeschrittener",
                        "Experte"
                    ],
                ("Ski Boots: Möchten Sie ein Modell aus einer bestimmten Preisklasse?", "ski-boots_möchten_sie_ein_modell_aus_einer_bestimmten_preisklasse"): [
                        "Budget (günstig & funktional)",
                        "Mittelklasse (ausgewogene Performance & Komfort)",
                        "Premium (höchste Qualität & Technologie)"
                    ],
                ("Ski Boots: Was suchen Sie?", "ski-boots_was_suchen_sie"): [
                        "Nur Skischuhe",
                        "Nur Ski",
                        "Komplettes Set (Ski & Skischuhe)"
                    ],
                ("Ski Boots: Wie eng soll der Skischuh sitzen?", "ski-boots_wie_eng_soll_der_skischuh_sitzen"): [
                        "Komfortabel (mehr Bewegungsfreiheit, wärmer)",
                        "Eng anliegend (bessere Kontrolle, aber weniger bequem)",
                        "Sehr eng (maximale Performance für Rennfahrer)"
                    ],
                ("Ski Boots: Welchen Flex bevorzugen Sie?", "ski-boots_welchen_flex_bevorzugen_sie"): [
                        "Weich (Flex 60–90, komfortabel für Einsteiger)",
                        "Mittel (Flex 90–110, ausgewogene Kontrolle)",
                        "Hart (Flex 120+, maximale Präzision für Profis)"
                    ],
                ("Ski Boots: Welche Körpergröße haben Sie?", "ski-boots_welche_körpergröße_haben_sie"): [
                        "Unter 160 cm",
                        "160-175 cm",
                        "176-190 cm",
                        "Über 190 cm"
                    ],
                ("Ski Boots: Wie viel wiegen Sie?", "ski-boots_wie_viel_wiegen_sie"): [
                        "Unter 60 kg",
                        "60-75 kg",
                        "76-90 kg",
                        "Über 90 kg"
                    ],
                ("Ski Boots: Wie lang sollten Ihre Ski sein?", "ski-boots_wie_lang_sollten_ihre_ski_sein"): [
                        "Kurze Ski – Leicht zu steuern, ideal für Anfänger und enge Slalom-Schwünge",
                        "Mittellange Ski – Gute Balance zwischen Kontrolle und Geschwindigkeit",
                        "Lange Ski – Mehr Stabilität bei hoher Geschwindigkeit, für erfahrene Skifahrer"
                    ],
                
                # ============ RUNNING SHOES - INITIAL ============
                ("Running Shoes: Für welchen Zweck suchen Sie die Laufschuhe?", "running-shoes_für_welchen_zweck_suchen_sie_die_laufschuhe?"): [
                        "Allrounder",
                        "Trailrunning (Gelände)",
                        "Lange Distanzen/Dauerläufe",
                        "Wettkampf/Marathon",
                        "Intervallläufe/Laufbahn",
                        "Walkingschuhe"
                    ],
                
                # ============ RUNNING SHOES - ALLROUNDER ============
                ("Running Shoes Allrounder: Wie bevorzugen Sie Ihre Allround - Laufschuhe zu tragen?", "running-shoes-allrounder_wie_bevorzugen_sie_ihre_allround_-_laufschuhe_zu_tragen"): [
                        "Die perfekte Laufschuh-passform basierend auf meinen 3D-Scan",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge",
                        "Eher enger, da ich meine Schuhe gern fest am Fuß trage"
                    ],
                ("Running Shoes Allrounder: Kennen Sie Ihren Fußtyp oder Ihre Pronation?", "running-shoes-allrounder_kennen_sie_ihren_fußtyp_oder_ihre_pronation"): [
                        "Analyse basierend auf meinem 3D-Scan",
                        "Neutralfuß",
                        "Überpronation (starker Einknick nach innen)"
                    ],
                ("Running Shoes Allrounder: Hatten Sie schon einmal Probleme oder Schmerzen beim Laufen?", "running-shoes-allrounder_hatten_sie_schon_einmal_probleme_oder_schmerzen_beim_laufen"): [
                        "Nein",
                        "Ja, Knieprobleme",
                        "Ja, Wadenprobleme",
                        "Ja, Shin Splints (Schienbeinschmerzen)",
                        "Ja, Plantarfasziitis (Fersenschmerzen)"
                    ],
                ("Running Shoes Allrounder: Welche Rolle spielt Dämpfung im Verhältnis zu Stabilität?", "running-shoes-allrounder_welche_rolle_spielt_dämpfung_im_verhältnis_zu_stabilität"): [
                        "Maximale Dämpfung – Fokus auf Komfort und Gelenkschonung",
                        "Ausgewogen – Gutes Verhältnis von Dämpfung und Stabilität",
                        "Mehr Stabilität – Fokus auf Kontrolle und Führung"
                    ],
                
                # ============ RUNNING SHOES - TRAILRUNNING ============
                ("Running Shoes Trailrunning: Wie bevorzugen Sie Ihre Trailrunning - Schuhe zu tragen?", "running-shoes-trailrunning_wie_bevorzugen_sie_ihre_trailrunning_-_schuhe_zu_tragen"): [
                        "Die perfekte Trailrunning-passform basierend auf meinen 3D-Scan",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge",
                        "Eher enger, da ich meine Schuhe gern fest am Fuß trage"
                    ],
                ("Running Shoes Trailrunning: Soll dein Schuh wasserdicht sein (Gore-Tex-Membran)?", "running-shoes-trailrunning_soll_dein_schuh_wasserdicht_sein_gore-tex-membran"): [
                        "Ja, wasserdicht und atmungsaktiv (Gore-Tex oder ähnliche Membran)",
                        "Nein, leichter und besser belüftet"
                    ],
                ("Running Shoes Trailrunning: Wo wirst du deine Trailrunning-Schuhe hauptsächlich nutzen?", "running-shoes-trailrunning_wo_wirst_du_deine_trailrunning-schuhe_hauptsächlich_nutzen"): [
                        "Nur auf Trails & im Gelände",
                        "Mischung aus Trail & Straße (Hybrid-Nutzung)"
                    ],
                ("Running Shoes Trailrunning: Welche Schafthöhe soll dein Schuh haben?", "running-shoes-trailrunning_welche_schafthöhe_soll_dein_schuh_haben"): [
                        "Niedrig (unter dem Knöchel)",
                        "Mittel/Hoch (knöchelhoch oder darüber)"
                    ],
                
                # ============ RUNNING SHOES - LONG DISTANCE ============
                ("Running Shoes Long Distance: Wie bevorzugen Sie Ihre Dauer - Laufschuhe zu tragen?", "running-shoes-longdistance_wie_bevorzugen_sie_ihre_dauer_-_laufschuhe_zu_tragen"): [
                        "Die perfekte Laufschuh-passform basierend auf meinen 3D-Scan",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge",
                        "Eher enger, da ich meine Schuhe gern fest am Fuß trage"
                    ],
                ("Running Shoes Long Distance: Auf welchem Untergrund wirst du hauptsächlich laufen?", "running-shoes-longdistance_auf_welchem_untergrund_wirst_du_hauptsächlich_laufen"): [
                        "Asphalt/Straße - Für regelmäßige, feste Oberflächen",
                        "Gemischt – Für unterschiedliche Oberflächen"
                    ],
                ("Running Shoes Long Distance: Hatten Sie schon einmal Probleme oder Schmerzen beim Laufen?", "running-shoes-longdistance_hatten_sie_schon_einmal_probleme_oder_schmerzen_beim_laufen"): [
                        "Nein",
                        "Ja, Knieprobleme",
                        "Ja, Wadenprobleme",
                        "Ja, Shin Splints (Schienbeinschmerzen)",
                        "Ja, Plantarfasziitis (Fersenschmerzen)"
                    ],
                ("Running Shoes Long Distance: Kennen Sie Ihren Fußtyp oder Ihre Pronation?", "running-shoes-longdistance_kennen_sie_ihren_fußtyp_oder_ihre_pronation"): [
                        "Analyse basierend auf meinem 3D-Scan",
                        "Neutralfuß",
                        "Überpronation (starker Einknick nach innen)"
                    ],
                ("Running Shoes Long Distance: Welche Rolle spielt Dämpfung im Verhältnis zu Stabilität?", "running-shoes-longdistance_welche_rolle_spielt_dämpfung_im_verhältnis_zu_stabilität"): [
                        "Maximale Dämpfung – Fokus auf Komfort und Gelenkschonung",
                        "Ausgewogen – Gutes Verhältnis von Dämpfung und Stabilität",
                        "Mehr Stabilität – Fokus auf Kontrolle und Führung"
                    ],
                
                # ============ RUNNING SHOES - COMPETITION ============
                ("Running Shoes Competition: Wie bevorzugen Sie Ihre Wettkampf - Schuhe zu tragen?", "running-shoes-competition_wie_bevorzugen_sie_ihre_wettkampf_-_schuhe_zu_tragen"): [
                        "Die perfekte Wettkampf-passform basierend auf meinen 3D-Scan",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge",
                        "Eher enger, da ich meine Schuhe gern fest am Fuß trage"
                    ],
                ("Running Shoes Competition: Welche Art von Wettkampfschuhen suchst du?", "running-shoes-competition_welche_art_von_wettkampfschuhen_suchst_du"): [
                        "Wettkampfschuhe Mit Carbon",
                        "Wettkampfschuhe Ohne Carbon"
                    ],
                ("Running Shoes Competition: Für welche Distanz suchst du Wettkampf-Schuhe?", "running-shoes-competition_für_welche_distanz_suchst_du_wettkampf-schuhe"): [
                        "Kurzstrecke (5 km – 10 km)",
                        "Halbmarathon (21,1 km)",
                        "Marathon (42,2 km & mehr)"
                    ],
                ("Running Shoes Competition: Welche Sprengung bevorzugst du?", "running-shoes-competition_welche_sprengung_bevorzugst_du"): [
                        "6–10 mm – Bewährte Wahl, unterstützt das Abrollen.",
                        "≤ 6 mm – Direkter Abdruck, erfordert trainierte Technik."
                    ],
                
                # ============ RUNNING SHOES - INTERVAL ============
                ("Running Shoes Interval: Wie bevorzugen Sie Ihre Intervall - Laufschuhe zu tragen?", "running-shoes-interval_wie_bevorzugen_sie_ihre_intervall_-_laufschuhe_zu_tragen"): [
                        "Die perfekte Intervall-passform basierend auf meinen 3D-Scan",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge"
                    ],
                ("Running Shoes Interval: Auf welchem Untergrund läufst du deine Intervalltrainings?", "running-shoes-interval_auf_welchem_untergrund_läufst_du_deine_intervalltrainings"): [
                        "Laufbahn (Spikes)",
                        "Asphalt/Laufbahn (ohne Spikes)"
                    ],
                ("Running Shoes Interval: Welche Distanz läufst du bei deinen Intervalltrainings?", "running-shoes-interval_welche_distanz_läufst_du_bei_deinen_intervalltrainings"): [
                        "Kurzstrecke (100–400 m)",
                        "Mittel- & Langstrecke (800 m – 10.000 m)"
                    ],
                
                # ============ RUNNING SHOES - WALKING ============
                ("Running Shoes Walking: Wie bevorzugen Sie Ihre Walking - Laufschuhe zu tragen?", "running-shoes-walking_wie_bevorzugen_sie_ihre_walking_-_laufschuhe_zu_tragen"): [
                        "Die perfekte Laufschuh-passform basierend auf meinen 3D-Scan",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge",
                        "Eher enger, da ich meine Schuhe gern fest am Fuß trage"
                    ],
                ("Running Shoes Walking: Auf welchem Untergrund wirst du hauptsächlich unterwegs sein?", "running-shoes-walking_auf_welchem_untergrund_wirst_du_hauptsächlich_unterwegs_sein"): [
                        "Harter Untergrund – Asphalt, Pflastersteine, Gehwege",
                        "Gemischtes Terrain – Abwechslung aus Natur- und Stadtwegen"
                    ],
                ("Running Shoes Walking: Bevorzugen Sie eine höhere Sohle oder eine normale bis mittlere Sohlenhöhe?", "running-shoes-walking_bevorzugen_sie_eine_höhere_sohle_oder_eine_normale_bis_mittlere_sohlenhöhe"): [
                        "Höhere Sohle – Fokus auf Komfort",
                        "Normale bis mittlere Sohle – Fokus auf nätürliches Abrollverhalten"
                    ],
                
                # ============ CLIMBING SHOES ============
                ("Climbing Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "climbing-shoes_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                        "Die empfohlene Kletterschuh-passform basierend auf meinen 3D-Scan",
                        "Eher weiter, für mehr Bewegungsfreiheit und höheren Tragekomfort"
                    ],
                ("Climbing Shoes: Wofür brauchst du die Kletterschuhe?", "climbing-shoes_wofür_brauchst_du_die_kletterschuhe"): [
                        "Mehrseillängen / Alpinklettern",
                        "Bouldern",
                        "Sportklettern",
                        "Rissklettern"
                    ],
                ("Climbing Shoes: Welche Fußform hast du?", "climbing-shoes_welche_fußform_hast_du"): [
                        "Ägyptisch",
                        "Römisch",
                        "Griechisch",
                        "Automatische Analyse laut Scan"
                    ],
                ("Climbing Shoes: Was ist dir bei der Sohle deines Kletterschuhs am wichtigsten?", "climbing-shoes_was_ist_dir_bei_der_sohle_deines_kletterschuhs_am_wichtigsten"): [
                        "Maximales Gefühl und Präzision",
                        "Unterstützung und Komfort",
                        "Langlebigkeit und Robustheit",
                        "Balance aus Haltbarkeit und Performance"
                    ],
                ("Climbing Shoes: Welche Form bevorzugen Sie?", "climbing-shoes_welche_form_bevorzugen_sie"): [
                        "Neutral – Komfortabel für lange Touren & Anfänger",
                        "Moderate Krümmung – Gute Balance aus Komfort & Präzision",
                        "Stark gekrümmt (Aggressiv) – Maximale Präzision für steile & schwierige Routen"
                    ],
                
                # ============ SOCCER SHOES ============
                ("Soccer Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "soccer-shoes_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                        "Die perfekte Fussballschuh-passform basierend auf meinen 3D-Scan",
                        "Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge"
                    ],
                ("Soccer Shoes: Auf welchem Untergrund spielst du hauptsächlich?", "soccer-shoes_auf_welchem_untergrund_spielst_du_hauptsächlich"): [
                        "Naturrasen (FG)",
                        "Kunstrasen (AG)",
                        "Halle (IC)"
                    ],
                ("Soccer Shoes: Was ist Ihnen wichtiger – Geschwindigkeit oder Stabilität?", "soccer-shoes_was_ist_ihnen_wichtiger_geschwindigkeit_oder_stabilität"): [
                        "Geschwindigkeit – Leichter Schuh für schnelle Antritte & Richtungswechsel.",
                        "Stabilität - Fester Sitz & Optimal für harte Zweikämpfe.",
                        "Vielseitigkeit – Balance aus Speed & Halt für flexible Spielstile."
                    ],
                ("Soccer Shoes: Welche Preisklasse bevorzugst du für deine Fußballschuhe?", "soccer-shoes_welche_preisklasse_bevorzugst_du_für_deine_fußballschuhe"): [
                        "Einsteiger-Modelle (€50 – €100)",
                        "Mittelklasse-Modelle (€100 – €200)",
                        "Premium-Modelle (über €200)"
                    ],
                }; 
            try:
                for q_label, ans_list in QUESTION_ANSWERS_MAP.items():
                    question_obj, created = Question.objects.get_or_create(
                        key=q_label[1],
                        defaults={"label": q_label[0]}
                    )
                    for ans_label in ans_list:
                        Answer.objects.get_or_create(
                            question=question_obj,
                            label=ans_label
                        )
            except OperationalError:
                pass
        post_migrate.connect(populate_questions, sender=self)