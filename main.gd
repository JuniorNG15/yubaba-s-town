extends Node2D

const HOTE := "127.0.0.1"
const PORT := 8765
const SECONDES_PAR_TOUR := 1.5
const COULEURS := {"S": Color("4caf50"), "I": Color("d62828"), "R": Color("3a86ff")}

class Habitant:
	var nom: String
	var pos: Vector2
	var cible: Vector2
	var etat: String = "S"
	var vitesse: float = 600.0

var batiments := {
	"Marché": {"zone": Rect2(110, 90, 230, 150), "entree": Vector2(225, 258), "couleur": Color("e0a458")},
	"École": {"zone": Rect2(460, 90, 200, 150), "entree": Vector2(560, 258), "couleur": Color("7fb7be")},
	"Atelier": {"zone": Rect2(800, 90, 200, 150), "entree": Vector2(900, 258), "couleur": Color("b08968")},
	"Dispensaire": {"zone": Rect2(780, 400, 220, 150), "entree": Vector2(890, 358), "couleur": Color("f4f1de")},
	"Puits": {"zone": Rect2(200, 430, 100, 100), "entree": Vector2(250, 358), "couleur": Color("6c91bf")},
}

var habitants := {}
var evenements_par_tour := {}
var tour_max := 0
var tour := 0
var minuteur := 0.0
var en_pause := false
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
				h.pos = point_dans(e["lieu"])
				h.cible = h.pos
				habitants[nom] = h
			"deplacement":
				if habitants.has(nom):
					habitants[nom].cible = point_dans(e["vers"])
			"contamination":
				if habitants.has(nom):
					habitants[nom].etat = "I"
			"guerison":
				if habitants.has(nom):
					habitants[nom].etat = "R"


func redemarrer() -> void:
	habitants.clear()
	tour = 0
	minuteur = 0.0


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_accept"):
		en_pause = not en_pause
	elif event is InputEventKey and event.pressed and event.keycode == KEY_R:
		redemarrer()


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
		draw_circle(h.pos, 11.0, COULEURS[h.etat])
		draw_arc(h.pos, 11.0, 0.0, TAU, 24, Color.BLACK, 2.0)
		draw_string(police, h.pos + Vector2(-30, -17), h.nom, HORIZONTAL_ALIGNMENT_CENTER, 60, 14, Color.BLACK)

	var etat_txt := "Yubaba's Town   Tour %d/%d   Sains: %d   Infectés: %d   Guéris: %d" % [tour, tour_max, c["S"], c["I"], c["R"]]
	draw_string(police, Vector2(20, 36), etat_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color.BLACK)
	var lien := "Pont Kafka : connecté" if connecte else "Pont Kafka : en attente (python backend\\pont.py)"
	draw_string(police, Vector2(20, 595), lien, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.BLACK)
	draw_string(police, Vector2(20, 620), "Espace = pause    R = recommencer", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.BLACK)
