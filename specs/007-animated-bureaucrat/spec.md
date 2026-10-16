# Feature Specification: Animated Bureaucrats

**Feature Branch**: `007-animated-bureaucrat`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Implementiere die Civil Servants als animierte Bureaucrat-Sprites mit einer Idle-Animation und einer Permit-Animation, die abhängig vom Zustand des jeweiligen Bureaucrats dauerhaft geloopt werden."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bureaucrats sichtbar animieren (Priority: P1)

Als Spieler möchte ich die Civil Servants als animierte Bureaucrat-Figuren sehen, damit die Welt lebendiger wirkt und die Personen klar von anderen Spielelementen unterscheidbar sind.

**Why this priority**: Die Bureaucrats sind zentrale Interaktionsziele des Spiels; ihre Darstellung muss auf Anhieb verständlich sein.

**Independent Test**: Das Spiel mit mindestens einem nicht bedienten Civil Servant starten und beobachten, dass statt des Platzhalter-Rechtecks die zweiframe Idle-Animation angezeigt wird.

**Acceptance Scenarios**:

1. **Given** ein Civil Servant ist nicht bedient, **When** der Spielbildschirm gerendert wird, **Then** erscheint das Bureaucrat-Sprite anstelle des bisherigen farbigen Rechtecks.
2. **Given** ein Civil Servant hat den Zustand `served=False`, **When** ausreichend Zeit vergeht, **Then** wechseln die beiden Idle-Frames wiederholt und unabhängig von der Render-Framerate.
3. **Given** mehrere nicht bediente Civil Servants existieren, **When** das Spiel gerendert wird, **Then** animiert jeder Civil Servant seine eigene Idle-Animation unabhängig von den anderen.

### User Story 2 - Erhaltenes Permit visuell darstellen (Priority: P1)

Als Spieler möchte ich erkennen, dass ein Bureaucrat mein Dokument beziehungsweise Permit akzeptiert hat, damit der Fortschritt des bürokratischen Ablaufs unmittelbar sichtbar ist.

**Why this priority**: Die Permit-Reaktion ist direktes Feedback für eine erfolgreiche Interaktion und unterstützt die Verständlichkeit der Wave-Aufgabe.

**Independent Test**: Einen Civil Servant erfolgreich bedienen und prüfen, dass seine Animation von Idle auf die zweiframe Permit-Animation wechselt und dort bleibt, solange er als bedient gilt.

**Acceptance Scenarios**:

1. **Given** ein Civil Servant ist nicht bedient und spielt die Idle-Animation, **When** ein gültiges Dokument erfolgreich übergeben wird, **Then** wechselt seine Darstellung zur Permit-Animation.
2. **Given** ein Civil Servant hat den Zustand `served=True`, **When** ausreichend Zeit vergeht, **Then** wiederholen sich die beiden Permit-Frames dauerhaft.
3. **Given** ein Civil Servant ist bereits beim Renderbeginn bedient, **When** er dargestellt wird, **Then** startet er direkt mit der Permit-Animation.
4. **Given** ein Civil Servant wechselt von `served=True` zu `served=False`, **When** der neue Zustand dargestellt wird, **Then** wechselt er zurück zur Idle-Animation.
5. **Given** mehrere Civil Servants werden nacheinander bedient, **When** die Permit-Animationen laufen, **Then** behält jeder Servant seinen eigenen Animationsfortschritt und Zustand.

### User Story 3 - Spielinformationen und Interaktion erhalten (Priority: P1)

Als Spieler möchte ich trotz der größeren Bureaucrat-Sprites weiterhin Servant-Nummern, Statusinformationen und Interaktionspositionen erkennen und verwenden können.

**Why this priority**: Die Animation darf die bestehende Bürokratie-Spielmechanik nicht unleserlich machen oder verändern.

**Independent Test**: Eine Wave mit mehreren Civil Servants starten, sie betrachten und bedienen und prüfen, dass Positionen, Interaktionen, Labels und bestehende UI-Anzeigen unverändert funktionieren.

**Acceptance Scenarios**:

1. **Given** Civil Servants sind im Spiel sichtbar, **When** ihre Sprites gerendert werden, **Then** bleiben Servant-Nummern und Statusinformationen lesbar.
2. **Given** ein Civil Servant wird als 84 × 128 Pixel großes Sprite dargestellt, **When** der Spieler mit ihm interagiert, **Then** bleiben seine logische Position und Interaktionsreichweite unverändert.
3. **Given** eine neue Wave beginnt, **When** ihre Civil Servants erscheinen, **Then** werden ihre Animationszustände aus dem jeweiligen `served`-Zustand korrekt initialisiert.
4. **Given** das Spiel zeigt Dokumente, Fishing, Countdown oder Game-Over-UI, **When** Bureaucrat-Sprites animiert werden, **Then** bleiben die bestehenden UI- und Overlay-Anzeigen funktionsfähig.

### Edge Cases

- Ein Bureaucrat mit `served=False` darf niemals die Permit-Animation anzeigen.
- Ein Bureaucrat mit `served=True` darf nicht zur Idle-Animation zurückfallen, solange dieser Zustand besteht.
- Der Wechsel der Animation darf nicht bei jedem Render-Aufruf neu beginnen.
- Ein bereits bedienter Bureaucrat muss auch nach einem erneuten Rendern oder einer Zustandsrekonstruktion die Permit-Animation verwenden.
- Eine Wave mit mehreren Bureaucrats darf keine gemeinsamen oder vermischten Frame-Zähler verwenden.
- Ein sehr großer Simulationsschritt darf keinen ungültigen Frame-Index erzeugen.
- Das größere Sprite darf weder die logische Interaktionsposition noch andere Spielelemente unerwartet verändern.
- Das Spritesheet darf nicht innerhalb jedes Render-Aufrufs erneut geladen oder ausgeschnitten werden.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Das Spiel MUST `assets/NPC/Bureaucrat/Bureaucrat-Sheet.png` als visuelle Darstellung der Civil Servants verwenden.
- **FR-002**: Das Asset MUST als Raster mit 2 Spalten und 2 Reihen behandelt werden; jeder Frame ist 84 × 128 Pixel groß.
- **FR-003**: Reihe 0, Spalten 0–1, MUST die zweiframe Idle-Animation bilden.
- **FR-004**: Reihe 1, Spalten 0–1, MUST die zweiframe Permit-Animation bilden.
- **FR-005**: Ein Civil Servant mit `served=False` MUST dauerhaft die Idle-Animation aus Reihe 0 wiederholen.
- **FR-006**: Ein Civil Servant mit `served=True` MUST dauerhaft die Permit-Animation aus Reihe 1 wiederholen.
- **FR-007**: Die aktive Animation MUST ausschließlich durch den aktuellen `served`-Zustand des jeweiligen Civil Servants bestimmt werden.
- **FR-008**: Jeder Civil Servant MUST einen eigenen Animationszustand mit eigenem Frame-Index und Zeitfortschritt besitzen.
- **FR-009**: Der Animationszustand MUST beim Wechsel des `served`-Zustands zur passenden Animation wechseln, ohne durch jeden Render-Aufruf zurückgesetzt zu werden.
- **FR-010**: Ein bereits bedienter Civil Servant MUST direkt mit der Permit-Animation initialisiert werden.
- **FR-011**: Die Animation MUST mit einer konstanten, framerate-unabhängigen Geschwindigkeit zwischen 2 und 4 Frames pro Sekunde laufen; als Standardwert werden 3 Frames pro Sekunde angenommen.
- **FR-012**: Das Spritesheet MUST einmal geladen und wiederverwendet werden; wiederholtes Laden oder Ausschneiden während des Renderns ist nicht zulässig.
- **FR-013**: Die bisherige Rechteckdarstellung der Civil Servants MUST durch das Bureaucrat-Sprite ersetzt werden.
- **FR-014**: Servant-Nummern, Statusinformationen und bestehendes UI-Feedback MUST weiterhin lesbar bleiben.
- **FR-015**: Das Sprite MUST horizontal auf der bestehenden Civil-Servant-Position zentriert und mit seiner Unterkante als Fußpunkt ausgerichtet werden.
- **FR-016**: Die logische Position, Interaktionsreichweite, Dokumentenlogik, Wave-Logik, Stamina, Fishing, Kamera und Game-Over-Funktion MUST unverändert bleiben.
- **FR-017**: Der Animationszustand MUST zur Präsentationsschicht gehören und darf keine zusätzliche spielregelbestimmende Bedeutung erhalten.
- **FR-018**: Frame-Auswahl, Zustandswechsel, Loop-Verhalten, unabhängige Servant-Zustände und Sprite-Ausrichtung MUSS durch automatisierte Tests abgedeckt werden.

### Key Entities

- **Bureaucrat Sprite Sheet**: Das vorhandene 2 × 2-Tileset mit vier Einzelbildern für Idle- und Permit-Animation.
- **Civil Servant**: Das bestehende Interaktionsziel mit ID, Position, Reihenfolge und `served`-Zustand.
- **Bureaucrat Animation State**: Der Präsentationszustand eines Servants mit aktiver Animation, Frame-Index und vergangener Frame-Zeit.
- **Idle Animation**: Der dauerhafte Zweiframe-Zyklus für `served=False`.
- **Permit Animation**: Der dauerhafte Zweiframe-Zyklus für `served=True`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100 % der Tests mit `served=False` wird ausschließlich ein Frame aus Reihe 0 verwendet.
- **SC-002**: In 100 % der Tests mit `served=True` wird ausschließlich ein Frame aus Reihe 1 verwendet.
- **SC-003**: Jeder der beiden Animationszustände durchläuft bei ausreichender Simulationszeit beide zugehörigen Frames mindestens einmal und wiederholt sie anschließend zyklisch.
- **SC-004**: Bei gleicher simulierter Zeit erreichen Animationen unabhängig von der Anzahl der Render-Schritte denselben Frame.
- **SC-005**: In einer Test-Wave mit mindestens drei Civil Servants können Idle- und Permit-Animationen gleichzeitig aktiv sein, ohne Frame-Zustände zu vermischen.
- **SC-006**: Nach einem erfolgreichen Dokumentenübergang wird beim betroffenen Civil Servant innerhalb eines Simulationsschritts die Permit-Animation sichtbar.
- **SC-007**: Sprite-Ausrichtung und Interaktionsposition stimmen in 100 % der geprüften Servant-Positionen überein; die bestehende Interaktionsreichweite wird nicht verändert.
- **SC-008**: Die bestehende Bürokratie-, Wave-, UI-, Fishing-, Stamina-, Kamera- und Game-Over-Test-Suite bleibt ohne durch dieses Feature verursachte Regressionen erfolgreich.
- **SC-009**: Bei manueller Prüfung mit dem Zielwert von 3 Frames pro Sekunde wirken beide Animationen bei 60 FPS gleichmäßig und ohne sichtbare Sprünge.

## Assumptions

- Das vorhandene PNG ist das maßgebliche Runtime-Asset; die Aseprite-Datei wird nicht zur Laufzeit benötigt.
- Die Idle-Animation ist für `served=False` und die Permit-Animation für `served=True` zuständig.
- Beide Animationen werden dauerhaft geloopt und nicht als einmalige Reaktionen abgespielt.
- Der Standardwert für die Animationsgeschwindigkeit beträgt 3 Frames pro Sekunde und kann über zentrale Konfiguration angepasst werden.
- Die bestehenden Civil-Servant-Positionen repräsentieren den Fußpunkt beziehungsweise die Mitte des Interaktionsziels; die Sprite-Ausrichtung verändert diese logische Position nicht.
- Die bestehenden Servant-Labels und Statusinformationen bleiben als ergänzendes UI-Feedback erhalten.
- Neue Waves erzeugen neue Präsentationszustände anhand des jeweiligen aktuellen `served`-Werts.
- Zusätzliche Richtungsvarianten, Spiegelungen oder weitere Bureaucrat-Typen sind nicht Bestandteil dieses Features.
