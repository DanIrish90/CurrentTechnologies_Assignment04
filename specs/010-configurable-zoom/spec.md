# Feature Specification: Configurable Start Zoom

**Feature Branch**: `010-configurable-zoom`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Einen Zoomstufenmultiplikator in der Konfiguration editierbar machen, damit die Startansicht fein abstimmbar und flexibel ist."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Startansicht fein abstimmen (Priority: P1)

Als Entwickler möchte ich einen zentralen Zoom-Multiplikator in der Konfiguration verändern können, damit ich die beim Spielstart sichtbare Ausschnittsgröße ohne Änderungen an Spielwelt oder Spiellogik fein einstellen kann.

**Why this priority**: Die gewünschte Startansicht ist der unmittelbare Nutzen der Funktion und muss unabhängig von weiteren Erweiterungen funktionieren.

**Independent Test**: Den Multiplikator auf mehrere Werte setzen, das Spiel jeweils starten und vergleichen, ob die Welt und alle sichtbaren Spielelemente entsprechend größer oder kleiner dargestellt werden.

**Acceptance Scenarios**:

1. **Given** der Multiplikator steht auf `1.0`, **When** das Spiel startet, **Then** bleibt die Darstellung gegenüber der bisherigen Ansicht unverändert.
2. **Given** der Multiplikator steht auf `2.0`, **When** das Spiel startet, **Then** wird ein entsprechend kleinerer Welt-Ausschnitt vergrößert dargestellt und der Spieler bleibt in der Startansicht sichtbar.
3. **Given** der Multiplikator steht auf `1.5`, **When** das Spiel startet, **Then** wird die Ansicht fein zwischen den ganzzahligen Zoomstufen skaliert, ohne dass eine weitere Codeänderung erforderlich ist.

### User Story 2 - Spielbarkeit bei jeder gültigen Zoomstufe erhalten (Priority: P1)

Als Spieler möchte ich mich unabhängig von der gewählten Zoomstufe bewegen und mit der Welt interagieren können, damit der Zoom nur die Darstellung verändert und keine Spielregeln verfälscht.

**Why this priority**: Ein Zoom, der Kollisionen, Interaktionen oder Kameragrenzen verändert, würde bestehendes Gameplay beschädigen.

**Independent Test**: Das Spiel mit mindestens den Werten `1.0`, `1.5` und `2.0` starten, an Weltgrenzen und Hindernissen bewegen sowie Dokument-, Fisch- und UI-Interaktionen ausführen.

**Acceptance Scenarios**:

1. **Given** eine gültige Zoomstufe ist gesetzt, **When** der Spieler sich bewegt, **Then** bleiben Geschwindigkeit, Kollisionen und Weltgrenzen spielmechanisch unverändert.
2. **Given** eine gültige Zoomstufe ist gesetzt, **When** der Spieler eine bestehende Interaktion ausführt, **Then** liegen Interaktionsbereiche weiterhin an ihren ursprünglichen Weltpositionen.
3. **Given** der Spieler bewegt sich durch die Welt, **When** die Kamera folgt, **Then** bleibt die Ansicht innerhalb der Welt und der Spieler bleibt sichtbar, sofern dies bei der jeweiligen Weltkante möglich ist.

### User Story 3 - Robuste und lesbare Darstellung erhalten (Priority: P2)

Als Spieler möchte ich bei einer zulässigen Zoomstufe eine lesbare und stabile Darstellung erhalten, damit UI, Figuren und wichtige Interaktionshinweise verständlich bleiben.

**Why this priority**: Feintuning ist nur nützlich, wenn der gewählte Wert keine leere, abgeschnittene oder unlesbare Startansicht erzeugt.

**Independent Test**: Das Spiel mit mehreren ganzzahligen und gebrochenen gültigen Werten sowie einer veränderten Fenstergröße starten und die Darstellung auf sichtbare UI, Spielstartposition und stabile Bildausgabe prüfen.

**Acceptance Scenarios**:

1. **Given** der Multiplikator liegt im gültigen Bereich, **When** das Spiel startet oder das Fenster angepasst wird, **Then** wird die Ansicht ohne Absturz, sichtbare ungerenderte Randbereiche oder ungewollte Spielzustandsänderung aktualisiert.
2. **Given** der Multiplikator ist ein gebrochener positiver Wert, **When** das Spiel startet, **Then** bleiben Figuren, Welt und UI vollständig sichtbar oder werden nach den definierten Kameraregeln nachvollziehbar begrenzt.
3. **Given** ein ungültiger Wert wie `0`, ein negativer, nicht endlicher oder nicht numerischer Wert wird verwendet, **When** das Spiel startet, **Then** wird der Start verhindert oder ein sicherer Standardwert verwendet und die Ursache verständlich gemeldet.

### Edge Cases

- Der Wert `1.0` muss die bisherige Darstellung und das bestehende Verhalten reproduzieren.
- Werte knapp über oder unter einer ganzen Zahl müssen ohne sichtbares Flackern oder unstabile Kamerapositionen funktionieren.
- Sehr hohe gültige Werte dürfen keine Division durch null, negative Ansichtsgröße oder Absturz verursachen.
- Ein Zoom, bei dem der sichtbare Bereich kleiner als die Welt ist, muss an Weltgrenzen korrekt begrenzt werden.
- Ein Zoom, bei dem der sichtbare Bereich größer als die Welt ist, darf keine Bereiche außerhalb der Welt als gültige Spielwelt ausgeben.
- Ein ungültiger Konfigurationswert darf keine teilweise initialisierte Spielsitzung hinterlassen.
- Das UI muss trotz Zoom als zusammenhängende Darstellung erkennbar bleiben und darf nicht unabhängig vom Spielbild an einer falschen Weltposition erscheinen.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Das Spiel MUST einen zentralen, beim Start editierbaren Zoom-Multiplikator bereitstellen.
- **FR-002**: Der Zoom-Multiplikator MUST positive Dezimalwerte unterstützen, damit Zwischenstufen wie `1.25`, `1.5` und `1.75` verwendet werden können.
- **FR-003**: Der Wert `1.0` MUST die bisherige Darstellung ohne zusätzliche Vergrößerung oder Verkleinerung herstellen.
- **FR-004**: Werte größer als `1.0` MUST die sichtbare Welt vergrößern, sodass ein kleinerer Welt-Ausschnitt auf der gleichen Startansicht erscheint.
- **FR-005**: Werte zwischen `0` und `1.0` MUST eine kleinere Darstellung ermöglichen, sofern sie innerhalb des zulässigen Konfigurationsbereichs liegen.
- **FR-006**: Die Zoomdarstellung MUST Weltkoordinaten, Spielerbewegung, Kollisionen, Interaktionsbereiche, Wellenfortschritt, Ausdauerregeln und Spielende unverändert lassen.
- **FR-007**: Die Kamera MUST den durch den Zoom veränderten sichtbaren Bereich weiterhin innerhalb der Weltgrenzen halten.
- **FR-008**: Die Startansicht MUST den Spieler an seiner bestehenden Startposition anzeigen und den initialen Spielzustand unverändert laden.
- **FR-009**: Welt, Figuren, UI und vorhandene Overlays MUST gemeinsam und konsistent skaliert beziehungsweise angeordnet werden, damit die Darstellung nicht auseinanderfällt.
- **FR-010**: Die Darstellung MUST bei ganzzahligen und gebrochenen gültigen Zoomwerten stabil bleiben und darf keine ungerenderten Flächen erzeugen.
- **FR-011**: Das Spiel MUST ungültige, nicht endliche oder nicht positive Multiplikatorwerte erkennen und entweder einen sicheren Standardwert verwenden oder den Start mit einer verständlichen Fehlermeldung ablehnen.
- **FR-012**: Der zulässige Bereich des Zoom-Multiplikators MUST dokumentiert und zentral auffindbar sein.
- **FR-013**: Die Zoomstufe MUST ohne Änderung an Karten-, Spawn- oder Interaktionsdaten angepasst werden können.
- **FR-014**: Die bestehende Fensteranpassung MUST weiterhin funktionieren, ohne Spielregeln oder den autoritativen Weltzustand zu verändern.

### Key Entities

- **Zoom-Multiplikator**: Eine positive, fein abstimmbare Darstellungseinstellung mit einem definierten Standardwert, zulässigem Wertebereich und der Bedeutung `1.0` als unveränderter Maßstab.
- **Sichtbarer Welt-Ausschnitt**: Der Bereich der Welt, der nach Anwendung des Zoom-Multiplikators in der Fensteransicht dargestellt wird.
- **Darstellungsebene**: Die gemeinsame sichtbare Ausgabe aus Welt, Spielfiguren, UI und temporären Overlays, die aus demselben Zoomkontext hervorgeht.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Eine Änderung des Zoom-Multiplikators erfordert für die Anpassung der Startansicht höchstens eine Konfigurationsänderung und keine Änderung an Karten-, Spawn- oder Spielregel-Daten.
- **SC-002**: Das Spiel startet mit den Referenzwerten `1.0`, `1.5` und `2.0` jeweils erfolgreich und erreicht die spielbare Ansicht ohne Absturz oder sichtbare ungerenderte Randbereiche.
- **SC-003**: In einem zehnminütigen manuellen Test bleiben Bewegung, Kollisionen, Kameraführung, Dokumentenübergaben, Fischen, Wellenwechsel und Neustart bei mindestens drei gültigen Zoomstufen funktionsfähig.
- **SC-004**: Bei `1.0` stimmen Startposition, sichtbarer Ausschnitt und Bedienbarkeit mit dem Verhalten vor Einführung der Funktion überein.
- **SC-005**: Ein gebrochener Referenzwert wie `1.25` kann ohne zusätzliche Programmänderung verwendet werden und erzeugt eine nachvollziehbar feinere Zoomstufe als `1.0`.
- **SC-006**: Jeder ungültige Referenzwert (`0`, negativ, nicht numerisch oder nicht endlich) führt zu einem kontrollierten Startverhalten mit verständlicher Rückmeldung und niemals zu einem ungefangenen Absturz.

## Assumptions

- Der Standardwert für die neue Startansicht wird auf `2.0` gesetzt, damit die Spielwelt beim Start deutlich größer lesbar ist; `1.0` bleibt der Kompatibilitäts- und Referenzwert.
- Der zulässige Wertebereich beginnt bei einem strikt positiven Wert und wird für Version 1 auf `0.5` bis `4.0` begrenzt, um unbrauchbare Ansichten und extreme Darstellungsanforderungen zu vermeiden.
- Die Einstellung gilt für die gesamte Darstellung einschließlich UI und temporärer Overlays, sofern die bestehende UI-Anordnung dadurch nicht unlesbar wird.
- Die Zoomstufe ist zunächst eine Startkonfiguration und muss während des laufenden Spiels nicht über ein Menü verändert werden.
- Pixelgenaue beziehungsweise stabile Darstellung ist wichtiger als eine zusätzliche Laufzeit-Zoomsteuerung.
- Die Funktion benötigt keine neuen externen Abhängigkeiten und muss die bestehende Desktop- und Offline-Ausrichtung erhalten.
