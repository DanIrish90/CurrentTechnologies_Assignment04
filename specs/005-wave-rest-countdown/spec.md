# Feature Specification: Wave Rest Countdown

**Feature Branch**: `005-wave-rest-countdown`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Nach Abschluss einer Wave beginnt eine 10-sekündige Ruhephase. Eine halbkreisförmige Countdown-Anzeige zeigt die verbleibende Zeit bis zur nächsten Wave. In der Mitte steht die Nummer der abgeschlossenen Wave. Die Uhr zeigt ihren Bogen nach oben und steht unten mittig im Bildschirm. Angeln ist ausschließlich während der Wave-Ruhephase möglich. Die nächste Wave startet automatisch bei null."

## Clarifications

### Session 2026-10-13

- Q: In welche Richtung soll der Halbkreis der Wave-Restuhr zeigen? → A: Der Bogen zeigt nach oben.
- Q: Soll Angeln während des aktiven Wave-Rest-Countdowns möglich sein? → A: Ja, Angeln ist während des Countdowns erlaubt.
- Q: Wo soll die Wave-Restuhr auf dem Bildschirm positioniert werden? → A: Zentriert am unteren Bildschirmrand.
- Q: Wann soll Angeln verfügbar sein? → A: Ausschließlich während der aktiven Wave-Ruhephase.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ruhephase und Countdown verstehen (Priority: P1)

Als Spieler möchte ich nach einer abgeschlossenen Wave sofort sehen, wie viel Vorbereitungszeit mir bis zur nächsten Wave bleibt, damit ich meine nächste Aktion planen kann.

**Why this priority**: Die Countdown-Anzeige erklärt den Übergang zwischen Waves und macht den Zeitdruck verständlich.

**Independent Test**: Eine Wave abschließen und prüfen, dass sofort eine klar erkennbare 10-sekündige Ruhephase mit Wave-Nummer, Halbkreis und verbleibender Zeit angezeigt wird.

**Acceptance Scenarios**:

1. **Given** alle Civil Servants der aktuellen Wave wurden bedient, **When** die Wave abgeschlossen wird, **Then** beginnt automatisch eine 10-sekündige Ruhephase.
2. **Given** die Ruhephase ist aktiv, **When** der Spieler die Anzeige betrachtet, **Then** sieht er die Nummer der abgeschlossenen Wave in der Mitte, eine gut lesbare Restzeit und einen halbkreisförmigen Countdown-Bogen.
3. **Given** die Ruhephase läuft, **When** Zeit vergeht, **Then** nimmt die angezeigte Restzeit kontinuierlich ab und der Countdown-Bogen leert sich entsprechend.

### User Story 2 - Angeln während der Ruhephase (Priority: P1)

Als Spieler möchte ich die Ruhephase zum Angeln nutzen können, um vor der nächsten Wave Stamina zurückzugewinnen.

**Why this priority**: Die Ruhephase ist das einzige Zeitfenster, in dem das Angel- und das Bürokratie-Spiel bewusst getrennt sind.

**Independent Test**: Eine Ruhephase starten, im Fishing Pond `E` drücken und prüfen, dass ein Angelversuch beginnt, während der Countdown weiterläuft; außerhalb der Ruhephase muss Angeln blockiert sein.

**Acceptance Scenarios**:

1. **Given** die Ruhephase ist aktiv und der Spieler steht leerhändig im Fishing Pond, **When** er `E` drückt, **Then** beginnt ein Angelversuch.
2. **Given** ein Angelversuch läuft während der Ruhephase, **When** der Countdown weiterläuft, **Then** nimmt die Restzeit unabhängig vom Angelinput kontinuierlich ab.
3. **Given** die nächste Wave ist aktiv, **When** der Spieler im Fishing Pond `E` drückt, **Then** wird kein Angelversuch gestartet.

### User Story 3 - Automatischer Übergang zur nächsten Wave (Priority: P1)

Als Spieler möchte ich, dass die nächste Wave automatisch startet, damit der Spielfluss ohne zusätzliche Eingabe fortgesetzt wird.

**Why this priority**: Der automatische Übergang hält die Eskalation des Bürokratie-Spiels aufrecht.

**Independent Test**: Eine Ruhephase bis auf null herunterlaufen lassen und prüfen, dass die nächste Wave einmalig startet und die Anzeige in den aktiven Wave-Zustand wechselt.

**Acceptance Scenarios**:

1. **Given** die Ruhephase ist aktiv, **When** die Restzeit null erreicht, **Then** startet automatisch genau die nächste Wave.
2. **Given** ein Angelversuch läuft beim Erreichen von null, **When** die nächste Wave startet, **Then** wird der Angelversuch ohne Fisch- oder Stamina-Belohnung abgebrochen.
3. **Given** die nächste Wave wurde gestartet, **When** der Spieler die Anzeige betrachtet, **Then** ist der Ruhephasen-Countdown nicht mehr sichtbar und die aktive Wave wird angezeigt.

### Edge Cases

- Der Countdown darf nicht unter null fallen und darf nicht mehr als einmal den Wave-Übergang auslösen.
- Ein Fang, der exakt mit dem Ablauf der Ruhephase zusammenfällt, erhält keine Belohnung, wenn der Wave-Übergang zuerst verarbeitet wird.
- Während einer aktiven Wave außerhalb der Ruhephase darf kein neuer Angelversuch gestartet werden.
- Die Anzeige muss auch bei sehr kurzen oder großen Simulationsschritten korrekt auf null begrenzt bleiben.
- Die erste Wave startet ohne vorherige Ruhephase und zeigt keinen abgeschlossenen Wave-Countdown.
- Neustart nach Game Over setzt die Ruhephase zurück und beginnt wieder mit der bestehenden Wave-1-Konfiguration.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Nach Abschluss einer Wave MUST das Spiel automatisch eine 10-sekündige Ruhephase starten.
- **FR-002**: Während der Ruhephase MUST die verbleibende Zeit als gut lesbare Zahl angezeigt werden.
- **FR-003**: Während der Ruhephase MUST ein halbkreisförmiger Countdown-Bogen den zeitlichen Fortschritt darstellen und sich kontinuierlich leeren.
- **FR-004**: Die Anzeige MUST die Nummer der gerade abgeschlossenen Wave im Zentrum des Halbkreises darstellen.
- **FR-005**: Der Countdown MUST unabhängig von Spielerinput kontinuierlich weiterlaufen.
- **FR-006**: Während der Ruhephase MUST ein leerhändiger Spieler im Fishing Pond angeln können.
- **FR-007**: Wenn die Restzeit null erreicht, MUST genau einmal die nächste Wave starten.
- **FR-008**: Wenn beim Ablauf der Ruhephase ein Angelversuch aktiv ist, MUST dieser ohne Fisch- oder Stamina-Belohnung abgebrochen werden.
- **FR-009**: Nach dem Wave-Übergang MUST die Ruhephasen-Anzeige ausgeblendet und der aktive Wave-Zustand angezeigt werden.
- **FR-010**: Die Ruhephase MUST die bestehende Wave-Reihenfolge, Civil-Servant-Anzahl, Dokumentenlogik, Stamina-Regeln, Game-Over-Regeln und Restart-Funktion erhalten.
- **FR-011**: Der Countdown MUST bei null begrenzt werden und darf keinen mehrfachen Wave-Übergang auslösen.
- **FR-012**: Die erste Wave MUST ohne vorherige Ruhephase starten.
- **FR-013**: Der Halbkreis MUST mit seiner offenen Seite nach unten zeigen, sodass der Bogen nach oben weist.
- **FR-014**: Die Wave-Restuhr MUST horizontal zentriert im unteren Bereich des Bildschirms erscheinen.
- **FR-015**: Während einer aktiven Wave außerhalb der Ruhephase MUST die Angelinteraktion blockiert sein, einschließlich des Castens im Fishing Pond.

### Key Entities

- **Wave Rest Phase**: Die zeitlich begrenzte Vorbereitungsphase zwischen zwei Waves mit einer Dauer von 10 Sekunden.
- **Wave Countdown**: Die sichtbare Restzeit und der halbkreisförmige Fortschrittsbogen der aktiven Ruhephase.
- **Wave Transition**: Der einmalige Übergang von der abgeschlossenen Wave zur nächsten Wave bei Ablauf des Countdowns.
- **Fishing Attempt**: Der bestehende Angelversuch, der ausschließlich während einer aktiven Wave-Ruhephase gestartet und fortgesetzt werden kann.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 20 abgeschlossenen Waves startet jedes Mal innerhalb eines Simulationsschritts die 10-sekündige Ruhephase mit sichtbarer Wave-Nummer und Restzeit.
- **SC-002**: In 20 kontrollierten Countdown-Tests sinkt die angezeigte Restzeit monoton von 10 Sekunden auf 0 und unterschreitet 0 nie.
- **SC-003**: In 20 Interaktionstests während der Ruhephase startet im Fishing Pond ein Angelversuch und der Countdown läuft weiter.
- **SC-004**: In 20 Übergangstests startet bei null genau eine nächste Wave; kein Test erzeugt einen doppelten Übergang.
- **SC-005**: In 20 erfolgreichen Angelversuchen während der Ruhephase wird die definierte Stamina-Belohnung vergeben; bei Ablauf der Ruhephase erhält ein gleichzeitig abgeschlossener Versuch keine Belohnung.
- **SC-006**: Mindestens 90 % der Testspieler können ohne Erklärung erkennen, welche Wave abgeschlossen wurde und wie viel Zeit bis zur nächsten Wave verbleibt.
- **SC-007**: Alle bestehenden Wave-, Dokument-, Fishing-, Stamina-, Game-Over- und Restart-Tests bleiben nach dem Countdown-Feature erfolgreich.

## Assumptions

- Die Ruhephase beginnt unmittelbar nach dem erfolgreichen Abschluss einer Wave und dauert in der ersten Version immer 10 Sekunden.
- Die erste Wave beginnt direkt im aktiven Spielzustand und benötigt keine Ruhephasen-Anzeige.
- Die bestehende Fishing-Pond-Interaktion und `E`-Steuerung werden ausschließlich während der Ruhephase verwendet; während einer aktiven Wave außerhalb der Ruhephase blockiert der Workflow den Angelstart.
- Die Ruhephase pausiert nicht durch Bewegung, Angeln, UI-Anzeige oder andere Spieleraktionen.
- Ein während der Ruhephase aktiver Angelversuch wird bei Ablauf ohne Belohnung beendet; der Wave-Übergang bei null hat Vorrang vor jedem gleichzeitig aufgelösten Angelzustand.
- Die Darstellung verwendet eine eigenständige, halbkreisförmige Fantasy-Spieluhr als visuelle Inspiration; externe Zelda-Assets oder identische Grafiken sind nicht erforderlich.
- Die bestehende Wave-Logik bestimmt weiterhin die Civil-Servant-Anzahl, Dokumentensequenzen und den Zustand der nächsten Wave.
