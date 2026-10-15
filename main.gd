extends Node2D

class Habitant:
	var nom: String
	var pos: Vector2
	var cible: Vector2
	var couleur: Color
	var vitesse: float
	var attente: float = 0.0

# zone = le bâtiment, entree = le point où les habitants viennent se placer
var batiments := {
	"Marché": {"zone": Rect2(110, 90, 230, 150), "entree": Vector2(225, 258), "couleur": Color("e0a458")},
	"École": {"zone": Rect2(460, 90, 200, 150), "entree": Vector2(560, 258), "couleur": Color("7fb7be")},
	"Atelier": {"zone": Rect2(800, 90, 200, 150), "entree": Vector2(900, 258), "couleur": Color("b08968")},
	"Dispensaire": {"zone": Rect2(780, 400, 220, 150), "entree": Vector2(890, 358), "couleur": Color("f4f1de")},
	"Puits": {"zone": Rect2(200, 430, 100, 100), "entree": Vector2(250, 358), "couleur": Color("6c91bf")},
}

var habitants: Array[Habitant] = []
var police := ThemeDB.fallback_font


func _ready() -> void:
	randomize()
	var noms := ["Mara", "Tomas", "Ilse", "Bram", "Noa"]
	var couleurs := [Color("d1495b"), Color("00798c"), Color("edae49"), Color("66a182"), Color("8d6cab")]
	for i in noms.size():
		var h := Habitant.new()
		h.nom = noms[i]
		h.couleur = couleurs[i]
		h.vitesse = randf_range(60.0, 110.0)
		h.pos = _entree_au_hasard()
		h.cible = h.pos
		h.attente = randf_range(0.0, 2.0)
		habitants.append(h)


func _entree_au_hasard() -> Vector2:
	var nom = batiments.keys().pick_random()
	var entree: Vector2 = batiments[nom]["entree"]
	return entree + Vector2(randf_range(-25.0, 25.0), randf_range(-8.0, 8.0))


func _process(delta: float) -> void:
	for h in habitants:
		if h.attente > 0.0:
			h.attente -= delta
			if h.attente <= 0.0:
				h.cible = _entree_au_hasard()
		else:
			h.pos = h.pos.move_toward(h.cible, h.vitesse * delta)
			if h.pos.is_equal_approx(h.cible):
				h.attente = randf_range(1.0, 4.0)
	queue_redraw()


func _draw() -> void:
	# Herbe et route
	draw_rect(Rect2(0, 0, 1152, 648), Color("a8c686"))
	draw_rect(Rect2(0, 270, 1152, 70), Color("8a8a8a"))

	# Titre
	draw_string(police, Vector2(20, 40), "Yubaba's Town — phase 1", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, Color.BLACK)

	# Bâtiments
	for nom in batiments:
		var zone: Rect2 = batiments[nom]["zone"]
		var couleur: Color = batiments[nom]["couleur"]
		draw_rect(zone, couleur)
		draw_rect(zone, couleur.darkened(0.4), false, 3.0)
		draw_string(police, Vector2(zone.position.x, zone.get_center().y + 7), nom, HORIZONTAL_ALIGNMENT_CENTER, zone.size.x, 22, Color.BLACK)

	# Habitants
	for h in habitants:
		draw_circle(h.pos, 10.0, h.couleur)
		draw_arc(h.pos, 10.0, 0.0, TAU, 24, Color.BLACK, 2.0)
		draw_string(police, h.pos + Vector2(-30, -16), h.nom, HORIZONTAL_ALIGNMENT_CENTER, 60, 14, Color.BLACK)
