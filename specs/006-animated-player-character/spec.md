# Feature Specification: Animated Player Character

**Feature Branch**: `006-animated-player-character`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Implementiere den Main Character als animierte Spielfigur aus dem vorhandenen Walking-Tileset, ohne Bewegungs-, Kollisions- oder Interaktionslogik zu verändern."

## Clarifications

### Session 2026-10-14

- Q: Soll die Figur bei Bewegung nach links die gespiegelte Seitenansicht und bei Bewegung nach rechts die originale Seitenansicht verwenden? → A: Nein: Bei Bewegung nach links wird die originale Seitenansicht verwendet, bei Bewegung nach rechts die gespiegelte Seitenansicht.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bewegungsrichtung visuell erkennen (Priority: P1)

Als Spieler möchte ich anhand der Figur sofort erkennen, in welche Richtung sie läuft, damit die Bewegung im Spiel verständlich bleibt.

**Why this priority**: Die Figur ist ein zentrales visuelles Feedback für jede Spielerbewegung.

**Independent Test**: Die Figur nacheinander nach oben, unten, rechts und links bewegen und prüfen, dass jeweils die passende Ansicht angezeigt wird.

**Acceptance Scenarios**:

1. **Given** der Spieler bewegt sich nach oben, **When** die Figur gerendert wird, **Then** wird die Rückenansicht angezeigt.
2. **Given** der Spieler bewegt sich nach unten, **When** die Figur gerendert wird, **Then** wird die Vorderansicht angezeigt.
3. **Given** der Spieler bewegt sich nach rechts, **When** die Figur gerendert wird, **Then** wird die seitliche Ansicht spiegelverkehrt angezeigt.
4. **Given** der Spieler bewegt sich nach links, **When** die Figur gerendert wird, **Then** wird die seitliche Ansicht mit normaler Ausrichtung angezeigt.
5. **Given** der Spieler bewegt sich diagonal, **When** die Figur gerendert wird, **Then** wird die Ansicht der Bewegungsachse mit der größeren absoluten Bewegung verwendet.

### User Story 2 - Laufanimation wahrnehmen (Priority: P1)

Als Spieler möchte ich während der Bewegung eine flüssige Laufanimation sehen, damit die Figur lebendig wirkt und Bewegung eindeutig von Stillstand unterscheidbar ist.

**Why this priority**: Die Laufanimation ist der eigentliche Mehrwert des vorhandenen Character-Assets und verbessert die Lesbarkeit der Bewegung.

**Independent Test**: Die Figur über mehrere aufeinanderfolgende Zeitintervalle bewegen und prüfen, dass alle vier Frames der passenden Animationsreihe zyklisch erscheinen.

**Acceptance Scenarios**:

1. **Given** der Spieler bewegt sich in eine Richtung, **When** ausreichend Zeit vergeht, **Then** wechseln die vier Frames der zugehörigen Reihe zyklisch.
2. **Given** die Bildwiederholrate ändert sich, **When** die gleiche Zeitspanne simuliert wird, **Then** bleibt der Animationsfortschritt gleich.
3. **Given** der Spieler steht still, **When** der aktuelle Frame bestimmt wird, **Then** wird der erste Frame der zuletzt verwendeten Blickrichtung angezeigt.
4. **Given** die Bewegungsrichtung wechselt, **When** die neue Bewegung beginnt, **Then** wird die Animation auf die passende Richtungsreihe umgestellt.

### User Story 3 - Sprite passend zur Spielfigur darstellen (Priority: P1)

Als Spieler möchte ich, dass die Füße der Figur korrekt auf der Spielfläche stehen und die bisherige Spielfigur-Darstellung ersetzt wird, damit die Grafik räumlich glaubwürdig bleibt.

**Why this priority**: Eine falsch ausgerichtete Figur würde Kollisionen und Interaktionen visuell widersprechen.

**Independent Test**: Das Spiel starten, die Figur an verschiedenen Positionen und an Hindernissen betrachten und prüfen, dass Sprite und logische Player-Position konsistent bleiben.

**Acceptance Scenarios**:

1. **Given** das Spiel startet, **When** der Spieler gerendert wird, **Then** erscheint das Main-Character-Sprite anstelle des bisherigen Rechtecks und der Beschriftung „YOU“.
2. **Given** die Figur befindet sich an einer beliebigen gültigen Position, **When** sie gerendert wird, **Then** ist das Sprite horizontal zentriert und seine Unterkante an der Unterkante der Player-Collisionbox ausgerichtet.
3. **Given** der Spieler kollidiert mit einem Hindernis, **When** die Darstellung aktualisiert wird, **Then** bleibt die bestehende Collisionbox maßgeblich und das Sprite verändert die Kollision nicht.
4. **Given** das Spiel läuft über viele Frames, **When** die Figur wiederholt gerendert wird, **Then** wird die Bilddatei nicht für jeden einzelnen Frame erneut geladen.

### Edge Cases

- Die Figur darf bei Stillstand nicht automatisch weiter animiert werden.
- Ein sehr großer Simulationsschritt darf den Animationszustand nicht in einen ungültigen Frame außerhalb der vier verfügbaren Frames bringen.
- Eine Bewegung gegen ein Hindernis darf nicht als erfolgreiche Bewegung animiert werden, wenn sich die Player-Position tatsächlich nicht verändert.
- Beim Wechsel von horizontaler Bewegung zu vertikaler Bewegung muss die zuletzt gültige Blickrichtung eindeutig aktualisiert werden.
- Beim Verlust des Fensterfokus dürfen keine inkonsistenten Bewegungs- oder Animationszustände entstehen.
- Die bestehende Darstellung der UI, der Civil Servants, der Dokumente, des Angel-Minispiels und des Wave-Countdowns darf nicht beeinträchtigt werden.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Das Spiel MUST das vorhandene Asset `assets/MainCharacter/MainCharacterWalking.png` als visuelle Darstellung des Main Characters verwenden.
- **FR-002**: Das Spiel MUST das Asset als Raster aus 4 Spalten und 3 Reihen mit 12 Einzelbildern behandeln; jedes Einzelbild ist 84 × 128 Pixel groß.
- **FR-003**: Reihe 0 MUST die Bewegung nach oben, Reihe 1 MUST die Bewegung nach unten und Reihe 2 MUST die seitliche Bewegung darstellen.
- **FR-004**: Während tatsächlicher Bewegung MUST die passende Reihe mit vier Frames zyklisch abgespielt werden.
- **FR-005**: Die Laufanimation MUST mit ungefähr 8 Frames pro Sekunde laufen und ihr Fortschritt MUST von der verstrichenen Simulationszeit statt von der Anzahl gerenderter Frames abhängen.
- **FR-006**: Horizontale Bewegung nach links MUST die unveränderte seitliche Ansicht verwenden; horizontale Bewegung nach rechts MUST die seitliche Ansicht spiegeln.
- **FR-007**: Bei diagonaler Bewegung MUST die Animationsrichtung anhand der Bewegungsachse mit der größeren absoluten Bewegung bestimmt werden.
- **FR-008**: Bei Stillstand MUST der erste Frame der zuletzt verwendeten Blickrichtung angezeigt werden.
- **FR-009**: Die zuletzt verwendete Blickrichtung MUST erhalten bleiben, wenn keine tatsächliche Bewegung stattfindet.
- **FR-010**: Die Darstellung MUST das Sprite horizontal zur Player-Collisionbox zentrieren und an deren Unterkante ausrichten.
- **FR-011**: Die Player-Collisionbox MUST unabhängig von Größe und Darstellung des Sprites bestehen bleiben und unverändert für Bewegung, Kollision und Interaktion verwendet werden.
- **FR-012**: Die bisherige Rechteckdarstellung des Spielers und die Beschriftung „YOU“ MUST durch das Sprite ersetzt werden.
- **FR-013**: Das Asset MUST einmal geladen und anschließend wiederverwendet werden; wiederholtes Laden während des Renderns ist nicht zulässig.
- **FR-014**: Animationszustand und Rendering MUST die deterministische Spiellogik nicht verändern.
- **FR-015**: Bewegungs-, Kollisions-, Interaktions-, Kamera-, UI-, Fishing-, Wave- und Game-Over-Verhalten MUST unverändert erhalten bleiben.
- **FR-016**: Die Auswahl von Richtung und Frame MUSS unabhängig testbar sein, einschließlich Richtungswechsel, Idle-Zustand, Spiegelung und großer Zeitintervalle.

### Key Entities

- **Main Character Sprite**: Das vorhandene Pixel-Art-Tileset mit zwölf visuellen Einzelbildern für drei Bewegungsansichten.
- **Character Direction**: Die zuletzt gültige Blickrichtung des Spielers: oben, unten, rechts oder links.
- **Animation State**: Der visuelle Zustand aus Bewegungsreihe, aktuellem Frame und zeitlichem Fortschritt.
- **Player Collisionbox**: Die unveränderte logische Fläche für Bewegung, Kollision und Interaktion; sie ist unabhängig vom Sprite.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In einem Richtungs-Test werden für oben, unten, rechts und links jeweils die korrekte Darstellung und Ausrichtung angezeigt.
- **SC-002**: In einer kontrollierten Laufanimation werden alle vier Frames jeder der drei Animationsreihen innerhalb eines vollständigen Zyklus genau einmal erreicht.
- **SC-003**: Bei gleicher simulierter Zeit erreicht die Animation unabhängig von der Anzahl der Render-Schritte denselben Frame.
- **SC-004**: In 100 % der getesteten Idle-Situationen wird der erste Frame der zuletzt verwendeten Blickrichtung angezeigt.
- **SC-005**: In 100 % der getesteten Kollisions- und Interaktionssituationen bleiben Player-Collisionbox, Bewegung, Kamera und Interaktion gegenüber dem bestehenden Verhalten unverändert.
- **SC-006**: Nach dem Start des Spiels ist der Main Character innerhalb des ersten sichtbaren Frames als Sprite statt als Platzhalter-Rechteck erkennbar.
- **SC-007**: Alle bestehenden automatisierten Tests sowie die neuen Tests zur Richtungs- und Frameauswahl bestehen erfolgreich.
- **SC-008**: Bei manueller Prüfung mit 60 FPS wirkt die Laufanimation kontinuierlich und zeigt keine sichtbaren Sprünge außerhalb der definierten vier Frames.

## Assumptions

- Das vorhandene PNG ist das maßgebliche Laufasset für die erste Version; zusätzliche Idle-, Lauf- oder diagonale Grafiken sind nicht Bestandteil dieses Features.
- Die drei Reihen werden in der Reihenfolge Rückenansicht, Vorderansicht und Seitenansicht interpretiert.
- Bei diagonaler Bewegung genügt die dominante Achse; es werden keine separaten diagonalen Animationen benötigt.
- Der erste Frame jeder Reihe ist der geeignete Stillstands-Frame.
- Die native Spritegröße von 84 × 128 Pixeln wird zunächst unverändert verwendet, sofern die bestehende Bildschirmdarstellung dadurch lesbar bleibt.
- Der Animationszustand ist Präsentationszustand und wird nicht gespeichert oder in Spielregeln einbezogen.
- Die vorhandene Bewegungslogik liefert die tatsächliche Positionsänderung beziehungsweise Bewegungsrichtung, damit blockierte Bewegungen nicht fälschlich als Laufbewegung dargestellt werden.
- Die bestehende Desktop-Spielarchitektur bleibt erhalten; zusätzliche Abhängigkeiten sind nicht erforderlich.
