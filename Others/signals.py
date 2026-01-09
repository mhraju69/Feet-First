from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Question, Answer
from django.db import OperationalError

@receiver(post_migrate)
def populate_questions(sender, **kwargs):
    if sender.label != "Others":
        return
    QUESTION_ANSWERS_MAP = {
        # ============ CYCLING SHOES ============
        ("Cycling Shoes: Welche Passform bevorzugst du?", "cycling-shoes_welche_passform_bevorzugst_du?"): [
                ("Enge, sportliche Passform (maximale Kraftübertragung)", "enge,_sportliche_passform_(maximale_kraftübertragung)"),
                ("Ausgewogene Passform (Kombination aus Performance und Komfort)", "ausgewogene_passform_(kombination_aus_performance_und_komfort)"),
                ("Bequeme Passform (mehr Platz und Komfort für Lange Fahrten)", "bequeme_passform_(mehr_platz_und_komfort_für_lange_fahrten)")
            ],
        ("Cycling Shoes: Welche Art von Radsport betreibst du?", "cycling-shoes_welche_art_von_radsport_betreibst_du?"): [
                ("Rennrad", "rennrad"),
                ("Mountainbike", "mountainbike"),
                ("Gravel", "gravel")
            ],
        ("Cycling Shoes: Welche Art von Pedalen benutzt du?", "cycling-shoes_welche_art_von_pedalen_benutzt_du?"): [
                ("Klickpedale", "klickpedale"),
                ("Plattformpedale", "plattformpedale"),
                ("Hybridpedale", "hybridpedale")
            ],
        ("Cycling Shoes: Welcher Steifigkeitsindex passt zu dir?", "cycling-shoes_welcher_steifigkeitsindex_passt_zu_dir?"): [
                ("5–7 – Mehr Flexibilität und Komfort, ideal für lange Touren & Gehen.", "5–7_–_mehr_flexibilität_und_komfort,_ideal_für_lange_touren_&_gehen."),
                ("8–10 – Perfekte Balance zwischen Komfort & Effizienz für Training & Rennen.", "8–10_–_perfekte_balance_zwischen_komfort_&_effizienz_für_training_&_rennen."),
                ("11–15 – Maximale Kraftübertragung für Wettkämpfe & explosive Sprints.", "11–15_–_maximale_kraftübertragung_für_wettkämpfe_&_explosive_sprints.")
            ],
        ("Cycling Shoes: Möchtest du mit einer individuell angepassten Winsole deine Performance auf das nächste Level heben?", "cycling-shoes_möchtest_du_mit_einer_individuell_angepassten_winsole_deine_performance_auf_das_nächste_level_heben?"): [
                ("Ja, für optimale Kraftübertragung und Bestleistung", "ja,_für_optimale_kraftübertragung_und_bestleistung"),
                ("Nein", "nein")
            ],
        
        # ============ CASUAL SHOES ============
        ("Casual Shoes: Welche Alltagsschuhe suchen sie?", "casual-sneaker_welche_alltagsschuhe_suchen_sie"): [
                ("Sneaker", "sneaker"),
                ("Anzugsschuhe", "anzugsschuhe"),
                ("Sportschuhe", "sportschuhe"),
                ("Sandalen", "sandalen"),
                ("Arbeitsschuhe", "arbeitsschuhe"),
                ("Bequemschuhe", "bequemschuhe")
            ],
        ("Casual Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "casual-sneaker_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                ("Die perfekt empfohlene Passform basierend auf meinem 3D-Scan", "die_perfekt_empfohlene_passform_basierend_auf_meinem_3d-scan"),
                ("Eher enger, da ich meine Schuhe gern fest am Fuß trage", "eher_enger_da_ich_meine_schuhe_gern_fest_am_fuß_trage"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge")
            ],
        ("Casual Shoes: Sind Sie im Besitz einer Orthopädischen Einlage?", "casual-sneaker_sind_sie_im_besitz_einer_orthopädischen_einlage"): [
                ("Ja", "ja"),
                ("Nein", "nein"),
                ("in Planung", "in_planung")
            ],
        
        # ============ MOUNTAIN/TREKKING SHOES ============
        ("Mountain/Trekking Shoes: Wie bevorzugen Sie Ihre Bergschuhe zu tragen?", "mountain-trekking-shoes_wie_bevorzugen_sie_ihre_bergschuhe_zu_tragen"): [
                ("Normale Passform – Ideal für Alltag und leichtere Touren.", "normale_passform_ideal_für_alltag_und_leichtere_touren"),
                ("Etwas weiter – für Bergtouren im Gebirge oder wenn du bewusst mehr Platz, z. B. für dicke Socken, wünschst.", "etwas_weiter_für_bergtouren_im_gebirge_oder_wenn_du_bewusst_mehr_platz_z_b_für_dicke_socken_wünschst")
            ],
        ("Mountain/Trekking Shoes: Auf welchem Untergrund werden Sie den Schuh hauptsächlich nutzen?", "mountain-trekking-shoes_auf_welchem_untergrund_werden_sie_den_schuh_hauptsächlich_nutzen"): [
                ("Alltag & leichte Wege – Stadt oder einfache Spaziergänge", "alltag_leichte_wege_stadt_oder_einfache_spaziergänge"),
                ("Normale Bergtouren – Wald- und Bergwege, auch uneben", "normale_bergtouren_wald-_und_bergwege_auch_uneben"),
                ("Hochtouren & alpines Gelände – felsig, steil oder hochalpin", "hochtouren_alpines_gelände_felsig_steil_oder_hochalpin")
            ],
        ("Mountain/Trekking Shoes: Welche Schafthöhe bevorzugen Sie?", "mountain-trekking-shoes_welche_schafthöhe_bevorzugen_sie"): [
                ("High-Cut – Maximaler Halt und Knöchelschutz für schwieriges Gelände.", "high-cut_maximaler_halt_und_knöchelschutz_für_schwieriges_gelände"),
                ("Mid-Cut – Gute Balance aus Beweglichkeit und Halt für vielseitige Touren.", "mid-cut_gute_balance_aus_beweglichkeit_und_halt_für_vielseitige_touren"),
                ("Low-Cut – Leicht und flexibel für schnelle, einfache Wege.", "low-cut_leicht_und_flexibel_für_schnelle_einfache_wege")
            ],
        ("Mountain/Trekking Shoes: Soll der Schuh wasserdicht sein?", "mountain-trekking-shoes_soll_der_schuh_wasserdicht_sein"): [
                ("Spielt keine entscheidende Rolle", "spielt_keine_entscheidende_rolle"),
                ("Atmungsaktive, nicht wasserdichte Schuhe", "atmungsaktive_nicht_wasserdichte_schuhe"),
                ("Wasserdichte Membran (z. B. Gore-Tex®)", "wasserdichte_membran_z_b_gore-tex")
            ],
        
        # ============ GOLF SHOES ============
        ("Golf Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "golf-shoes_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                ("Die perfekt empfohlene Golfschuh-Passform basierend auf meinem 3D-Scan", "die_perfekt_empfohlene_golfschuh-passform_basierend_auf_meinem_3d-scan"),
                ("Eher enger, da ich meine Schuhe gern fest am Fuß trage", "eher_enger_da_ich_meine_schuhe_gern_fest_am_fuß_trage"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge")
            ],
        ("Golf Shoes: Spikes oder Spikeless – Welcher Sohlen-Typ benötigst du?", "golf-shoes_spikes_oder_spikeless_welcher_sohlen-typ_benötigst_du"): [
                ("Spikeless", "spikeless"),
                ("Spikes", "spikes")
            ],
        ("Golf Shoes: Wie wichtig sind Wasserdichtigkeit und Atmungsaktivität bei deinen Golfschuhen?", "golf-shoes_wie_wichtig_sind_wasserdichtigkeit_und_atmungsaktivität_bei_deinen_golfschuhen"): [
                ("Maximale Wasserdichtigkeit, weniger Atmungsaktivität", "maximale_wasserdichtigkeit_weniger_atmungsaktivität"),
                ("Gute Balance zwischen wasserdicht & atmungsaktiv", "gute_balance_zwischen_wasserdicht_&_atmungsaktiv"),
                ("Keine Wasserdichtigkeit nötig, maximale Belüftung", "keine_wasserdichtigkeit_nötig_maximale_belüftung")
            ],
        ("Golf Shoes: Was ist dir wichtiger – Stabilität oder Komfort?", "golf-shoes_was_ist_dir_wichtiger_stabilität_oder_komfort"): [
                ("Stabilität – Sicherer Halt & maximale Kontrolle beim Schwung", "stabilität_sicherer_halt_&_maximale_kontrolle_beim_schwung"),
                ("Komfort – Längere Runden", "komfort_längere_runden")
            ],
        
        # ============ BASKETBALL SHOES ============
        ("Basketball Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "basketball-shoes_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                ("Die perfekte Baskettball-schuhpassform basierend auf meinen 3D-Scan", "die_perfekte_baskettball-schuhpassform_basierend_auf_meinen_3d-scan"),
                ("Eher enger, da ich meine Schuhe gern fest am Fuß trage", "eher_enger_da_ich_meine_schuhe_gern_fest_am_fuß_trage"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge")
            ],
        ("Basketball Shoes: Traktion & Grip – Wie ist der Untergrund?", "basketball-shoes_traktion_&_grip_wie_ist_der_untergrund"): [
                ("Indoor-Halle", "indoor-halle"),
                ("Outdoor", "outdoor")
            ],
        ("Basketball Shoes: Brauchst du mehr Knöchelschutz oder mehr Bewegungsfreiheit?", "basketball-shoes_brauchst_du_mehr_knöchelschutz_oder_mehr_bewegungsfreiheit"): [
                ("Viel Schutz (High-Tops)", "viel_schutz_high-tops"),
                ("Balance (Mid-Tops)", "balance_mid-tops"),
                ("Bewegungsfreiheit (Low-Tops)", "bewegungsfreiheit_low-tops")
            ],
        
        # ============ TENNIS SHOES ============
        ("Tennis Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "tennis-shoes_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                ("Die perfekte Tennisschuh-passform basierend auf meinen 3D-Scan", "die_perfekte_tennisschuh-passform_basierend_auf_meinen_3d-scan"),
                ("Eher enger, da ich meine Schuhe gern fest am Fuß trage", "eher_enger_da_ich_meine_schuhe_gern_fest_am_fuß_trage"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge")
            ],
        ("Tennis Shoes: Auf welchem Belag spielen Sie hauptsächlich?", "tennis-shoes_auf_welchem_belag_spielen_sie_hauptsächlich"): [
                ("Sandplatz/Claycourt", "sandplatz_claycourt"),
                ("Hartplatz/Allcourt", "hartplatz_allcourt"),
                ("Rasenplatz", "rasenplatz")
            ],
        ("Tennis Shoes: Ist dir Performance oder Langlebigkeit wichtiger?", "tennis-shoes_ist_dir_performance_oder_langlebigkeit_wichtiger"): [
                ("Maximale Performance (Leichter, agiler Schuh für schnelle Bewegungen)", "maximale_performance_leichter_agiler_schuh_für_schnelle_bewegungen"),
                ("Langlebigkeit & Strapazierfähigkeit (Robustere Materialien für längere Haltbarkeit)", "langlebigkeit_&_strapazierfähigkeit_robustere_materialien_für_längere_haltbarkeit")
            ],
        ("Tennis Shoes: Wie bewegst du dich auf dem Platz am meisten?", "tennis-shoes_wie_bewegst_du_dich_auf_dem_platz_am_meisten"): [
                ("Seitlich – Häufige Seitwärtsbewegungen", "seitlich_häufige_seitwärtsbewegungen"),
                ("Vor & zurück – Viele schnelle Sprints", "vor_&_zurück_viele_schnelle_sprints"),
                ("Beides – Ein guter Mix aus beiden", "beides_ein_guter_mix_aus_beiden")
            ],
        
        # ============ SKI BOOTS ============
        ("Ski Boots: Sind Sie Anfänger, Fortgeschrittener oder Experte?", "ski-boots_sind_sie_anfänger_fortgeschrittener_oder_experte"): [
                ("Anfänger", "anfänger"),
                ("Fortgeschrittener", "fortgeschrittener"),
                ("Experte", "experte")
            ],
        ("Ski Boots: Möchten Sie ein Modell aus einer bestimmten Preisklasse?", "ski-boots_möchten_sie_ein_modell_aus_einer_bestimmten_preisklasse"): [
                ("Budget (günstig & funktional)", "budget_günstig_und_funktional"),
                ("Mittelklasse (ausgewogene Performance & Komfort)", "mittelklasse_ausgewogene_performance_und_komfort"),
                ("Premium (höchste Qualität & Technologie)", "premium_höchste_qualität_und_technologie")
            ],
        ("Ski Boots: Was suchen Sie?", "ski-boots_was_suchen_sie"): [
                ("Nur Skischuhe", "nur_skischuhe"),
                ("Nur Ski", "nur_ski"),
                ("Komplettes Set (Ski & Skischuhe)", "komplettes_set_ski_und_skischuhe")
            ],
        ("Ski Boots: Wie eng soll der Skischuh sitzen?", "ski-boots_wie_eng_soll_der_skischuh_sitzen"): [
                ("Komfortabel (mehr Bewegungsfreiheit, wärmer)", "komfortabel_mehr_bewegungsfreiheit_wärmer"),
                ("Eng anliegend (bessere Kontrolle, aber weniger bequem)", "eng_anliegend_bessere_kontrolle_aber_weniger_bequem"),
                ("Sehr eng (maximale Performance für Rennfahrer)", "sehr_eng_maximale_performance_für_rennfahrer")
            ],
        ("Ski Boots: Welchen Flex bevorzugen Sie?", "ski-boots_welchen_flex_bevorzugen_sie"): [
                ("Weich (Flex 60–90, komfortabel für Einsteiger)", "weich_flex_60–90_komfortabel_für_einsteiger"),
                ("Mittel (Flex 90–110, ausgewogene Kontrolle)", "mittel_flex_90–110_ausgewogene_kontrolle"),
                ("Hart (Flex 120+, maximale Präzision für Profis)", "hart_flex_120+_maximale_präzision_für_profis")
            ],
        ("Ski Boots: Welche Körpergröße haben Sie?", "ski-boots_welche_körpergröße_haben_sie"): [
                ("Unter 150 cm", "under_150_cm"),
                ("150-160 cm", "150_160_cm"),
                ("160-170 cm", "160_170_cm"),
                ("170-180 cm", "170_180_cm"),
                ("180-190 cm", "180_190_cm"),
                ("190-200 cm", "190_200_cm"),
                ("Über 200 cm", "over_200_cm")
            ],
        ("Ski Boots: Wie viel wiegen Sie?", "ski-boots_wie_viel_wiegen_sie"): [
                ("Unter 50 kg", "under_50_kg"),
                ("50-60 kg", "50_60_kg"),
                ("60-70 kg", "60_70_kg"),
                ("70-80 kg", "70_80_kg"),
                ("80-90 kg", "80_90_kg"),
                ("90-100 kg", "90_100_kg"),
                ("100-110 kg", "100_110_kg"),
                ("Über 110 kg", "over_110_kg")
            ],
        ("Ski Boots: Wie lang sollten Ihre Ski sein?", "ski-boots_wie_lang_sollten_ihre_ski_sein"): [
                ("Kurze Ski – Leicht zu steuern, ideal für Anfänger und enge Slalom-Schwünge", "kurze_ski_leicht_zu_steuern_ideal_für_anfänger_und_enge_slalom-schwünge"),
                ("Mittellange Ski – Gute Balance zwischen Kontrolle und Geschwindigkeit", "mittellange_ski_gute_balance_zwischen_kontrolle_und_geschwindigkeit"),
                ("Lange Ski – Mehr Stabilität bei hoher Geschwindigkeit, für erfahrene Skifahrer", "lange_ski_mehr_stabilität_bei_hoher_geschwindigkeit_für_erfahrene_skifahrer")
            ],
        
        # ============ RUNNING SHOES - INITIAL ============
        ("Running Shoes: Für welchen Zweck suchen Sie die Laufschuhe?", "running-shoes_für_welchen_zweck_suchen_sie_die_laufschuhe?"): [
                ("Allrounder", "allrounder"),
                ("Trailrunning (Gelände)", "trailrunning_gelände"),
                ("Lange Distanzen/Dauerläufe", "lange_distanzen_dauerläufe"),
                ("Wettkampf/Marathon", "wettkampf_marathon"),
                ("Intervallläufe/Laufbahn", "intervallläufe_laufbahn"),
                ("Walkingschuhe", "walkingschuhe")
            ],
        
        # ============ RUNNING SHOES - ALLROUNDER ============
        ("Running Shoes Allrounder: Wie bevorzugen Sie Ihre Allround - Laufschuhe zu tragen?", "running-shoes-allrounder_wie_bevorzugen_sie_ihre_allround_-_laufschuhe_zu_tragen"): [
                ("Die perfekte Laufschuh-passform basierend auf meinen 3D-Scan", "die_perfekte_laufschuh-passform_basierend_auf_meinen_3d-scan"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge"),
                ("Eher enger, da ich meine Schuhe gern fest am Fuß trage", "eher_enger_da_ich_meine_schuhe_gern_fest_am_fuß_trage")
            ],
        ("Running Shoes Allrounder: Kennen Sie Ihren Fußtyp oder Ihre Pronation?", "running-shoes-allrounder_kennen_sie_ihren_fußtyp_oder_ihre_pronation"): [
                ("Analyse basierend auf meinem 3D-Scan", "analyse_basierend_auf_meinem_3d-scan"),
                ("Neutralfuß", "neutralfuß"),
                ("Überpronation (starker Einknick nach innen)", "überpronation_starker_einknick_nach_innen")
            ],
        ("Running Shoes Allrounder: Hatten Sie schon einmal Probleme oder Schmerzen beim Laufen?", "running-shoes-allrounder_hatten_sie_schon_einmal_probleme_oder_schmerzen_beim_laufen"): [
                ("Nein", "nein"),
                ("Ja, Knieprobleme", "ja_knieprobleme"),
                ("Ja, Wadenprobleme", "ja_wadenprobleme"),
                ("Ja, Shin Splints (Schienbeinschmerzen)", "ja_shin_splints_schienbeinschmerzen"),
                ("Ja, Plantarfasziitis (Fersenschmerzen)", "ja_plantarfasziitis_fersenschmerzen")
            ],
        ("Running Shoes Allrounder: Welche Rolle spielt Dämpfung im Verhältnis zu Stabilität?", "running-shoes-allrounder_welche_rolle_spielt_dämpfung_im_verhältnis_zu_stabilität"): [
                ("Maximale Dämpfung – Fokus auf Komfort und Gelenkschonung", "maximale_dämpfung_fokus_auf_komfort_und_gelenkschonung"),
                ("Ausgewogen – Gutes Verhältnis von Dämpfung und Stabilität", "ausgewogen_gutes_verhältnis_von_dämpfung_und_stabilität"),
                ("Mehr Stabilität – Fokus auf Kontrolle und Führung", "mehr_stabilität_fokus_auf_kontrolle_und_führung")
            ],
        
        # ============ RUNNING SHOES - TRAILRUNNING ============
        ("Running Shoes Trailrunning: Wie bevorzugen Sie Ihre Trailrunning - Schuhe zu tragen?", "running-shoes-trailrunning_wie_bevorzugen_sie_ihre_trailrunning_-_schuhe_zu_tragen"): [
                ("Die perfekte Trailrunning-passform basierend auf meinen 3D-Scan", "die_perfekte_trailrunning-passform_basierend_auf_meinen_3d-scan"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge"),
                ("Eher enger, da ich meine Schuhe gern fest am Fuß trage", "eher_enger_da_ich_meine_schuhe_gern_fest_am_fuß_trage")
            ],
        ("Running Shoes Trailrunning: Soll dein Schuh wasserdicht sein (Gore-Tex-Membran)?", "running-shoes-trailrunning_soll_dein_schuh_wasserdicht_sein_gore-tex-membran"): [
                ("Ja, wasserdicht und atmungsaktiv (Gore-Tex oder ähnliche Membran)", "ja_wasserdicht_und_atmungsaktiv_gore-tex_oder_ähnliche_membran"),
                ("Nein, leichter und besser belüftet", "nein_leichter_und_besser_belüftet")
            ],
        ("Running Shoes Trailrunning: Wo wirst du deine Trailrunning-Schuhe hauptsächlich nutzen?", "running-shoes-trailrunning_wo_wirst_du_deine_trailrunning-schuhe_hauptsächlich_nutzen"): [
                ("Nur auf Trails & im Gelände", "nur_auf_trails_und_im_gelände"),
                ("Mischung aus Trail & Straße (Hybrid-Nutzung)", "mischung_aus_trail_und_straße_hybrid-nutzung")
            ],
        ("Running Shoes Trailrunning: Welche Schafthöhe soll dein Schuh haben?", "running-shoes-trailrunning_welche_schafthöhe_soll_dein_schuh_haben"): [
                ("Niedrig (unter dem Knöchel)", "niedrig_unter_dem_knöchel"),
                ("Mittel/Hoch (knöchelhoch oder darüber)", "mittel_hoch_knöchelhoch_oder_darüber")
            ],
        
        # ============ RUNNING SHOES - LONG DISTANCE ============
        ("Running Shoes Long Distance: Wie bevorzugen Sie Ihre Dauer - Laufschuhe zu tragen?", "running-shoes-longdistance_wie_bevorzugen_sie_ihre_dauer_-_laufschuhe_zu_tragen"): [
                ("Die perfekte Laufschuh-passform basierend auf meinen 3D-Scan", "die_perfekte_laufschuh-passform_basierend_auf_meinen_3d-scan"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge"),
                ("Eher enger, da ich meine Schuhe gern fest am Fuß trage", "eher_enger_da_ich_meine_schuhe_gern_fest_am_fuß_trage")
            ],
        ("Running Shoes Long Distance: Auf welchem Untergrund wirst du hauptsächlich laufen?", "running-shoes-longdistance_auf_welchem_untergrund_wirst_du_hauptsächlich_laufen"): [
                ("Asphalt/Straße - Für regelmäßige, feste Oberflächen", "asphalt_straße_für_regelmäßige_feste_oberflächen"),
                ("Gemischt – Für unterschiedliche Oberflächen", "gemischt_für_unterschiedliche_oberflächen")
            ],
        ("Running Shoes Long Distance: Hatten Sie schon einmal Probleme oder Schmerzen beim Laufen?", "running-shoes-longdistance_hatten_sie_schon_einmal_probleme_oder_schmerzen_beim_laufen"): [
                ("Nein", "nein"),
                ("Ja, Knieprobleme", "ja_knieprobleme"),
                ("Ja, Wadenprobleme", "ja_wadenprobleme"),
                ("Ja, Shin Splints (Schienbeinschmerzen)", "ja_shin_splints_schienbeinschmerzen"),
                ("Ja, Plantarfasziitis (Fersenschmerzen)", "ja_plantarfasziitis_fersenschmerzen")
            ],
        ("Running Shoes Long Distance: Kennen Sie Ihren Fußtyp oder Ihre Pronation?", "running-shoes-longdistance_kennen_sie_ihren_fußtyp_oder_ihre_pronation"): [
                ("Analyse basierend auf meinem 3D-Scan", "analyse_basierend_auf_meinem_3d-scan"),
                ("Neutralfuß", "neutralfuß"),
                ("Überpronation (starker Einknick nach innen)", "überpronation_starker_einknick_nach_innen")
            ],
        ("Running Shoes Long Distance: Welche Rolle spielt Dämpfung im Verhältnis zu Stabilität?", "running-shoes-longdistance_welche_rolle_spielt_dämpfung_im_verhältnis_zu_stabilität"): [
                ("Maximale Dämpfung – Fokus auf Komfort und Gelenkschonung", "maximale_dämpfung_fokus_auf_komfort_und_gelenkschonung"),
                ("Ausgewogen – Gutes Verhältnis von Dämpfung und Stabilität", "ausgewogen_gutes_verhältnis_von_dämpfung_und_stabilität"),
                ("Mehr Stabilität – Fokus auf Kontrolle und Führung", "mehr_stabilität_fokus_auf_kontrolle_und_führung")
            ],
        
        # ============ RUNNING SHOES - COMPETITION ============
        ("Running Shoes Competition: Wie bevorzugen Sie Ihre Wettkampf - Schuhe zu tragen?", "running-shoes-competition_wie_bevorzugen_sie_ihre_wettkampf_-_schuhe_zu_tragen"): [
                ("Die perfekte Wettkampf-passform basierend auf meinen 3D-Scan", "die_perfekte_wettkampf-passform_basierend_auf_meinen_3d-scan"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge"),
                ("Eher enger, da ich meine Schuhe gern fest am Fuß trage", "eher_enger_da_ich_meine_schuhe_gern_fest_am_fuß_trage")
            ],
        ("Running Shoes Competition: Welche Art von Wettkampfschuhen suchst du?", "running-shoes-competition_welche_art_von_wettkampfschuhen_suchst_du"): [
                ("Wettkampfschuhe Mit Carbon", "wettkampfschuhe_mit_carbon"),
                ("Wettkampfschuhe Ohne Carbon", "wettkampfschuhe_ohne_carbon")
            ],
        ("Running Shoes Competition: Für welche Distanz suchst du Wettkampf-Schuhe?", "running-shoes-competition_für_welche_distanz_suchst_du_wettkampf-schuhe"): [
                ("Kurzstrecke (5 km – 10 km)", "kurzstrecke_5_km_–_10_km"),
                ("Halbmarathon (21,1 km)", "halbmarathon_21_1_km"),
                ("Marathon (42,2 km & mehr)", "marathon_42_2_km_und_mehr")
            ],
        ("Running Shoes Competition: Welche Sprengung bevorzugst du?", "running-shoes-competition_welche_sprengung_bevorzugst_du"): [
                ("6–10 mm – Bewährte Wahl, unterstützt das Abrollen.", "6–10_mm_bewährte_wahl_unterstützt_das_abrollen"),
                ("≤ 6 mm – Direkter Abdruck, erfordert trainierte Technik.", "≤_6_mm_direkter_abdruck_erfordert_trainierte_technik")
            ],
        
        # ============ RUNNING SHOES - INTERVAL ============
        ("Running Shoes Interval: Wie bevorzugen Sie Ihre Intervall - Laufschuhe zu tragen?", "running-shoes-interval_wie_bevorzugen_sie_ihre_intervall_-_laufschuhe_zu_tragen"): [
                ("Die perfekte Intervall-passform basierend auf meinen 3D-Scan", "die_perfekte_intervall-passform_basierend_auf_meinen_3d-scan"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge")
            ],
        ("Running Shoes Interval: Auf welchem Untergrund läufst du deine Intervalltrainings?", "running-shoes-interval_auf_welchem_untergrund_läufst_du_deine_intervalltrainings"): [
                ("Laufbahn (Spikes)", "laufbahn_spikes"),
                ("Asphalt/Laufbahn (ohne Spikes)", "asphalt_laufbahn_ohne_spikes")
            ],
        ("Running Shoes Interval: Welche Distanz läufst du bei deinen Intervalltrainings?", "running-shoes-interval_welche_distanz_läufst_du_bei_deinen_intervalltrainings"): [
                ("Kurzstrecke (100–400 m)", "kurzstrecke_100–400_m"),
                ("Mittel- & Langstrecke (800 m – 10.000 m)", "mittel-_und_langstrecke_800_m_–_10_000_m")
            ],
        
        # ============ RUNNING SHOES - WALKING ============
        ("Running Shoes Walking: Wie bevorzugen Sie Ihre Walking - Laufschuhe zu tragen?", "running-shoes-walking_wie_bevorzugen_sie_ihre_walking_-_laufschuhe_zu_tragen"): [
                ("Die perfekte Laufschuh-passform basierend auf meinen 3D-Scan", "die_perfekte_laufschuh-passform_basierend_auf_meinen_3d-scan"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge"),
                ("Eher enger, da ich meine Schuhe gern fest am Fuß trage", "eher_enger_da_ich_meine_schuhe_gern_fest_am_fuß_trage")
            ],
        ("Running Shoes Walking: Auf welchem Untergrund wirst du hauptsächlich unterwegs sein?", "running-shoes-walking_auf_welchem_untergrund_wirst_du_hauptsächlich_unterwegs_sein"): [
                ("Harter Untergrund – Asphalt, Pflastersteine, Gehwege", "harter_untergrund_asphalt_pflastersteine_gehwege"),
                ("Gemischtes Terrain – Abwechslung aus Natur- und Stadtwegen", "gemischtes_terrain_abwechslung_aus_natur-_und_stadtwegen")
            ],
        ("Running Shoes Walking: Bevorzugen Sie eine höhere Sohle oder eine normale bis mittlere Sohlenhöhe?", "running-shoes-walking_bevorzugen_sie_eine_höhere_sohle_oder_eine_normale_bis_mittlere_sohlenhöhe"): [
                ("Höhere Sohle – Fokus auf Komfort", "höhere_sohle_fokus_auf_komfort"),
                ("Normale bis mittlere Sohle – Fokus auf nätürliches Abrollverhalten", "normale_bis_mittlere_sohle_fokus_auf_nätürliches_abrollverhalten")
            ],
        
        # ============ CLIMBING SHOES ============
        ("Climbing Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "climbing-shoes_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                ("Die empfohlene Kletterschuh-passform basierend auf meinen 3D-Scan", "die_empfohlene_kletterschuh-passform_basierend_auf_meinen_3d-scan"),
                ("Eher weiter, für mehr Bewegungsfreiheit und höheren Tragekomfort", "eher_weiter_für_mehr_bewegungsfreiheit_und_höheren_tragekomfort")
            ],
        ("Climbing Shoes: Wofür brauchst du die Kletterschuhe?", "climbing-shoes_wofür_brauchst_du_die_kletterschuhe"): [
                ("Mehrseillängen / Alpinklettern", "mehrseillängen_/_alpinklettern"),
                ("Bouldern", "bouldern"),
                ("Sportklettern", "sportklettern"),
                ("Rissklettern", "rissklettern")
            ],
        ("Climbing Shoes: Welche Fußform hast du?", "climbing-shoes_welche_fußform_hast_du"): [
                ("Ägyptisch", "ägyptisch"),
                ("Römisch", "römisch"),
                ("Griechisch", "griechisch"),
                ("Automatische Analyse laut Scan", "automatische_analyse_laut_scan")
            ],
        ("Climbing Shoes: Was ist dir bei der Sohle deines Kletterschuhs am wichtigsten?", "climbing-shoes_was_ist_dir_bei_der_sohle_deines_kletterschuhs_am_wichtigsten"): [
                ("Maximales Gefühl und Präzision", "maximales_gefühl_und_präzision"),
                ("Unterstützung und Komfort", "unterstützung_und_komfort"),
                ("Langlebigkeit und Robustheit", "langlebigkeit_und_robustheit"),
                ("Balance aus Haltbarkeit und Performance", "balance_aus_haltbarkeit_und_performance")
            ],
        ("Climbing Shoes: Welche Form bevorzugen Sie?", "climbing-shoes_welche_form_bevorzugen_sie"): [
                ("Neutral – Komfortabel für lange Touren & Anfänger", "neutral_komfortabel_für_lange_touren_&_anfänger"),
                ("Moderate Krümmung – Gute Balance aus Komfort & Präzision", "moderate_krümmung_gute_balance_aus_komfort_&_präzision"),
                ("Stark gekrümmt (Aggressiv) – Maximale Präzision für steile & schwierige Routen", "stark_gekrümmt_aggressiv_maximale_präzision_für_steile_&_schwierige_routen")
            ],
        
        # ============ SOCCER SHOES ============
        ("Soccer Shoes: Wie bevorzugen Sie Ihre Schuhe zu tragen?", "soccer-shoes_wie_bevorzugen_sie_ihre_schuhe_zu_tragen"): [
                ("Die perfekte Fussballschuh-passform basierend auf meinen 3D-Scan", "die_perfekte_fussballschuh-passform_basierend_auf_meinen_3d-scan"),
                ("Eher weiter, da ich mehr Bewegungsfreiheit bevorzuge", "eher_weiter_da_ich_mehr_bewegungsfreiheit_bevorzuge")
            ],
        ("Soccer Shoes: Auf welchem Untergrund spielst du hauptsächlich?", "soccer-shoes_auf_welchem_untergrund_spielst_du_hauptsächlich"): [
                ("Naturrasen (FG)", "naturrasen_fg"),
                ("Kunstrasen (AG)", "kunstrasen_ag"),
                ("Halle (IC)", "halle_ic")
            ],
        ("Soccer Shoes: Was ist Ihnen wichtiger – Geschwindigkeit oder Stabilität?", "soccer-shoes_was_ist_ihnen_wichtiger_geschwindigkeit_oder_stabilität"): [
                ("Geschwindigkeit – Leichter Schuh für schnelle Antritte & Richtungswechsel.", "geschwindigkeit_leichter_schuh_für_schnelle_antritte_&_richtungswechsel"),
                ("Stabilität - Fester Sitz & Optimal für harte Zweikämpfe.", "stabilität_-_fester_sitz_&_optimal_für_harte_zweikämpfe"),
                ("Vielseitigkeit – Balance aus Speed & Halt für flexible Spielstile.", "vielseitigkeit_balance_aus_speed_&_halt_für_flexible_spielstile")
            ],
        ("Soccer Shoes: Welche Preisklasse bevorzugst du für deine Fußballschuhe?", "soccer-shoes_welche_preisklasse_bevorzugst_du_für_deine_fußballschuhe"): [
                ("Einsteiger-Modelle (€50 – €100)", "einsteiger-modelle_€50_–_€100"),
                ("Mittelklasse-Modelle (€100 – €200)", "mittelklasse-modelle_€100_–_€200"),
                ("Premium-Modelle (über €200)", "premium-modelle_über_€200")
            ],
        }; 
    try:
        for q_label, ans_list in QUESTION_ANSWERS_MAP.items():
            question_obj, created = Question.objects.get_or_create(
                key=q_label[1],
                defaults={"label": q_label[0]}
            )
            for ans_tuple in ans_list:
                Answer.objects.get_or_create(
                    question=question_obj,
                    key= ans_tuple[1],
                    defaults={"label": ans_tuple[0]}
                )
    except OperationalError:
        pass
