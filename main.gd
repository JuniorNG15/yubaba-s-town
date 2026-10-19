extends Node2D

const HOTE := "127.0.0.1"
const PORT := 8765
const SECONDES_PAR_TOUR := 1.5
const COULEURS := {"S": Color("4caf50"), "I": Color("d62828"), "R": Color("3a86ff")}
const ETATS := {"S": "sain", "I": "infecté", "R": "guéri"}

class Habitant:
	var nom: String
	var role: String = ""
	var quartier: String = ""
	var lieu: String = "Maison"
	var pos: Vector2
	var cible: Vector2
	var etat: String = "S"
	var confiance: float = 0.5
	var croyance_puits: float = 0.0
	var croyance_contact: float = 0.0
	var regle: String = "(aucune décision encore)"
	var detail: String = ""
	var souvenirs: Array = []
	var vitesse: float = 600.0

var batiments := {
	"Marché": {"zone": Rect2(110, 90, 230, 150), "entree": Vector2(225, 258), "couleur": Color("e0a458")},
	"École": {"zone": Rect2(460, 90, 200, 150), "entree": Vector2(560, 258), "couleur": Color("7fb7be")},
	"Atelier": {"zone": Rect2(800, 90, 200, 150), "entree": Vector2(900, 258), "couleur": Color("b08968")},
	"Dispensaire": {"zone": Rect2(780, 400, 220, 150), "entree": Vector2(890, 358), "couleur": Color("f4f1de")},
	"Puits": {"zone": Rect2(200, 430, 100, 100), "entree": Vector2(250, 358), "couleur": Color("6c91bf")},
	"Maison": {"zone": Rect2(450, 400, 200, 150), "entree": Vector2(550, 358), "couleur": Color("d9c5b2")},
}

var habitants := {}
var evenements_par_tour := {}
var tour_max := 0
var tour := 0
var minuteur := 0.0
var en_pause := false
var selection := ""
var police := ThemeDB.fallback_font

var tcp := StreamPeerTCP.new()
var tampon := PackedByteArray()
var connecte := false
var prochain_essai := 0.0


func _ready() -> void:
	randomize()
	se_connecter()


func se_connecter() -> void:
	tcp = StreamPeerTCP.new()
	tampon = PackedByteArray()
	tcp.connect_to_host(HOTE, PORT)


func lire_reseau(delta: float) -> void:
	tcp.poll()
	match tcp.get_status():
		StreamPeerTCP.STATUS_CONNECTED:
			if not connecte:
				connecte = true
				vider()  # nouvelle connexion : le pont rejoue tout depuis le début
			var n := tcp.get_available_bytes()
			if n > 0:
				var r := tcp.get_data(n)
				if r[0] == OK:
					tampon.append_array(r[1])
					traiter_tampon()
		StreamPeerTCP.STATUS_NONE, StreamPeerTCP.STATUS_ERROR:
			connecte = false
			prochain_essai -= delta
			if prochain_essai <= 0.0:
				prochain_essai = 2.0
				se_connecter()


func traiter_tampon() -> void:
	var idx := tampon.rfind(10)  # 10 = retour à la ligne
	if idx < 0:
		return
	var complet := tampon.slice(0, idx + 1)
	tampon = tampon.slice(idx + 1)
	for ligne in complet.get_string_from_utf8().split("\n", false):
		ajouter_evenement(ligne)


func ajouter_evenement(ligne: String) -> void:
	var e = JSON.parse_string(ligne)
	if not (e is Dictionary):
		return
	var t := int(e["tour"])
	if not evenements_par_tour.has(t):
		evenements_par_tour[t] = []
	evenements_par_tour[t].append(e)
	tour_max = max(tour_max, t)


func vider() -> void:
	evenements_par_tour.clear()
	tour_max = 0
	redemarrer()


func point_dans(lieu: String) -> Vector2:
	var entree: Vector2 = batiments[lieu]["entree"]
	return entree + Vector2(randf_range(-30.0, 30.0), randf_range(-10.0, 10.0))


func appliquer_tour(t: int) -> void:
	for e in evenements_par_tour.get(t, []):
		var nom: String = e["habitant"]
		match e["type"]:
			"init":
				var h := Habitant.new()
				h.nom = nom
				h.etat = e["etat"]
				h.role = e.get("role", "")
				h.quartier = e.get("quartier", "")
				h.confiance = float(e.get("confiance", 0.5))
				h.croyance_puits = float(e.get("croyance_puits", 0.0))
				h.croyance_contact = float(e.get("croyance_contact", 0.0))
				h.lieu = e["lieu"]
				h.pos = point_dans(h.lieu)
				h.cible = h.pos
				habitants[nom] = h
			"deplacement":
				if habitants.has(nom):
					habitants[nom].lieu = e["vers"]
					habitants[nom].cible = point_dans(e["vers"])
			"contamination":
				if habitants.has(nom):
					habitants[nom].etat = "I"
			"guerison":
				if habitants.has(nom):
					habitants[nom].etat = "R"
			"decision":
				if habitants.has(nom):
					habitants[nom].regle = e["regle"]
					habitants[nom].detail = e["detail"]
			"souvenir":
				if habitants.has(nom):
					habitants[nom].souvenirs.append("tour %d : %s" % [t, e["detail"]])
					if habitants[nom].souvenirs.size() > 3:
						habitants[nom].souvenirs.pop_front()
			"croyance":
				if habitants.has(nom):
					if e["cible"] == "puits":
						habitants[nom].croyance_puits = float(e["valeur"])
					else:
						habitants[nom].croyance_contact = float(e["valeur"])


func redemarrer() -> void:
	habitants.clear()
	tour = 0
	minuteur = 0.0


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_accept"):
		en_pause = not en_pause
	elif event is InputEventKey and event.pressed and event.keycode == KEY_R:
		redemarrer()
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		selection = ""
		var p := get_local_mouse_position()
		for h in habitants.values():
			if h.pos.distance_to(p) < 22.0:
				selection = h.nom


func _process(delta: float) -> void:
	lire_reseau(delta)
	if habitants.is_empty() and evenements_par_tour.has(0):
		appliquer_tour(0)
	if not en_pause:
		minuteur += delta
		if minuteur >= SECONDES_PAR_TOUR and tour < tour_max:
			minuteur = 0.0
			tour += 1
			appliquer_tour(tour)
		for h in habitants.values():
			h.pos = h.pos.move_toward(h.cible, h.vitesse * delta)
	queue_redraw()


func _draw() -> void:
	draw_rect(Rect2(0, 0, 1152, 648), Color("a8c686"))
	draw_rect(Rect2(0, 270, 1152, 70), Color("8a8a8a"))

	for nom in batiments:
		var zone: Rect2 = batiments[nom]["zone"]
		var couleur: Color = batiments[nom]["couleur"]
		draw_rect(zone, couleur)
		draw_rect(zone, couleur.darkened(0.4), false, 3.0)
		draw_string(police, Vector2(zone.position.x, zone.get_center().y + 7), nom, HORIZONTAL_ALIGNMENT_CENTER, zone.size.x, 22, Color.BLACK)

	var c := {"S": 0, "I": 0, "R": 0}
	for h in habitants.values():
		c[h.etat] += 1
		if h.croyance_puits > 0.5:
			draw_arc(h.pos, 17.0, 0.0, TAU, 24, Color("ff9500"), 3.0)  # rumeur du puits
		draw_circle(h.pos, 11.0, COULEURS[h.etat])
		draw_arc(h.pos, 11.0, 0.0, TAU, 24, Color.BLACK, 2.0)
		draw_string(police, h.pos + Vector2(-30, -22), h.nom, HORIZONTAL_ALIGNMENT_CENTER, 60, 14, Color.BLACK)

	var etat_txt := "Yubaba's Town   Tour %d/%d   Sains: %d   Infectés: %d   Guéris: %d" % [tour, tour_max, c["S"], c["I"], c["R"]]
	draw_string(police, Vector2(20, 36), etat_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color.BLACK)
	draw_string(police, Vector2(20, 64), "Cercle : vert sain, rouge infecté, bleu guéri     Anneau orange : croit le puits contaminé", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.BLACK)

	var lien := "Pont Kafka : connecté" if connecte else "Pont Kafka : en attente (python backend\\pont.py)"
	draw_string(police, Vector2(20, 595), lien, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.BLACK)
	draw_string(police, Vector2(20, 620), "Espace = pause   R = recommencer   Clic = détails", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.BLACK)

	if selection != "" and habitants.has(selection):
		var s = habitants[selection]
		draw_arc(s.pos, 21.0, 0.0, TAU, 32, Color.BLACK, 3.0)
		draw_rect(Rect2(470, 470, 670, 172), Color(1, 1, 1, 0.92))
		draw_string(police, Vector2(480, 492), "%s — %s (quartier %s) — %s — lieu : %s" % [s.nom, s.role, s.quartier, ETATS[s.etat], s.lieu], HORIZONTAL_ALIGNMENT_LEFT, 650, 17, Color.BLACK)
		draw_string(police, Vector2(480, 515), "confiance dispensaire %.2f    croyance contacts %.2f    croyance puits %.2f" % [s.confiance, s.croyance_contact, s.croyance_puits], HORIZONTAL_ALIGNMENT_LEFT, 650, 17, Color.BLACK)
		draw_string(police, Vector2(480, 538), "Règle appliquée : %s — %s" % [s.regle, s.detail], HORIZONTAL_ALIGNMENT_LEFT, 650, 17, Color.BLACK)
		draw_string(police, Vector2(480, 565), "Derniers souvenirs marquants :", HORIZONTAL_ALIGNMENT_LEFT, 650, 17, Color.BLACK)
		var y := 586.0
		if s.souvenirs.is_empty():
			draw_string(police, Vector2(490, y), "(aucun pour l'instant)", HORIZONTAL_ALIGNMENT_LEFT, 640, 16, Color.BLACK)
		for m in s.souvenirs:
			draw_string(police, Vector2(490, y), m, HORIZONTAL_ALIGNMENT_LEFT, 640, 16, Color.BLACK)
			y += 20.0
