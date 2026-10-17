# Feature Specification: Wave Rest Countdown

**Feature Branch**: `005-wave-rest-countdown`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Nach Abschluss einer Wave beginnt eine konfigurierbare Ruhephase. Ein animierter Wurm bewegt sich unterhalb der StaminaBar von links nach rechts und zeigt die verbleibende Zeit bis zur nächsten Wave. Angeln ist ausschließlich während der Wave-Ruhephase möglich. Die nächste Wave startet automatisch bei null."

## Clarifications

### Session 2026-10-13

- Q: Soll Angeln während des aktiven Wave-Rest-Countdowns möglich sein? → A: Ja, Angeln ist während des Countdowns erlaubt.
- Q: Wann soll Angeln verfügbar sein? → A: Ausschließlich während der aktiven Wave-Ruhephase.

### Session 2026-10-17

- Q: Soll die Ruhephasendauer weiterhin standardmäßig 10 Sekunden betragen, aber ausschließlich über eine zentrale Config-Variable (z. B. `WAVE_REST_DURATION`) geändert werden können? → A: Ja; Standardwert 10 Sekunden, die Config-Variable bestimmt die tatsächliche Ruhephasendauer.
- Q: Soll die konfigurierbare WormTimer-Animationsgeschwindigkeit die Anzahl der Sprite-Frames pro Sekunde bestimmen? → A: Ja; der Config-Wert wird als Sprite-Frames pro Sekunde angegeben.
- Q: Soll sich der Wurm während jeder Ruhephase unabhängig von der Sprite-Animation proportional zur verstrichenen Ruhezeit von links nach rechts unter der StaminaBar bewegen und am Ende exakt rechts ankommen? → A: Ja; die Position folgt dem Ruhephasenfortschritt, die Sprite-Frames laufen unabhängig davon.
- Q: Soll `WormTimer.png` als horizontales Sprite-Sheet mit 14 gleich großen 32×32-Frames verwendet werden, die während der Ruhephase fortlaufend wiederholt werden? → A: 7 horizontale 64×32-Frames, fortlaufend wiederholt.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ruhephase und Countdown verstehen (Priority: P1)

Als Spieler möchte ich nach einer abgeschlossenen Wave sofort sehen, wie viel Vorbereitungszeit mir bis zur nächsten Wave bleibt, damit ich meine nächste Aktion planen kann.

**Why this priority**: Die Countdown-Anzeige erklärt den Übergang zwischen Waves und macht den Zeitdruck verständlich.

**Independent Test**: Eine Wave abschließen und prüfen, dass sofort eine klar erkennbare Ruhephase mit einem animierten WormTimer unterhalb der StaminaBar beginnt.

**Acceptance Scenarios**:

1. **Given** alle Civil Servants der aktuellen Wave wurden bedient, **When** die Wave abgeschlossen wird, **Then** beginnt automatisch eine Ruhephase mit der in der zentralen Config festgelegten Dauer, standardmäßig 10 Sekunden.
2. **Given** die Ruhephase ist aktiv, **When** der Spieler die Anzeige betrachtet, **Then** sieht er den animierten WormTimer unterhalb der StaminaBar.
3. **Given** die Ruhephase läuft, **When** Zeit vergeht, **Then** bewegt sich der Wurm proportional von links nach rechts unterhalb der StaminaBar und erreicht bei Ablauf deren rechtes Ende.

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

- **FR-001**: Nach Abschluss einer Wave MUST das Spiel automatisch eine Ruhephase mit der zentralen Config-Dauer `WAVE_REST_DURATION` starten; der Standardwert MUSS 10 Sekunden betragen.
- **FR-002**: Während der Ruhephase MUST der animierte WormTimer unterhalb der StaminaBar sichtbar sein.
- **FR-003**: Der WormTimer MUST den zeitlichen Fortschritt durch die proportionale Bewegung des Wurms von links nach rechts unterhalb der StaminaBar darstellen.
- **FR-004**: Der WormTimer MUST bei Ablauf der Ruhephase das rechte Ende der StaminaBar erreichen.
- **FR-005**: Der Countdown MUST unabhängig von Spielerinput kontinuierlich weiterlaufen.
- **FR-006**: Während der Ruhephase MUST ein leerhändiger Spieler im Fishing Pond angeln können.
- **FR-007**: Wenn die Restzeit null erreicht, MUST genau einmal die nächste Wave starten.
- **FR-008**: Wenn beim Ablauf der Ruhephase ein Angelversuch aktiv ist, MUST dieser ohne Fisch- oder Stamina-Belohnung abgebrochen werden.
- **FR-009**: Nach dem Wave-Übergang MUST die Ruhephasen-Anzeige ausgeblendet und der aktive Wave-Zustand angezeigt werden.
- **FR-010**: Die Ruhephase MUST die bestehende Wave-Reihenfolge, Civil-Servant-Anzahl, Dokumentenlogik, Stamina-Regeln, Game-Over-Regeln und Restart-Funktion erhalten.
- **FR-011**: Der Countdown MUST bei null begrenzt werden und darf keinen mehrfachen Wave-Übergang auslösen.
- **FR-012**: Die erste Wave MUST ohne vorherige Ruhephase starten.
- **FR-013**: Während einer aktiven Wave außerhalb der Ruhephase MUST die Angelinteraktion blockiert sein, einschließlich des Castens im Fishing Pond.
- **FR-014**: Der WormTimer MUST während der Ruhephase als Animation aus `WormTimer.png` mit sieben horizontalen 64×32-Frames dargestellt werden; die Frames MÜSSEN fortlaufend wiederholt werden.
- **FR-015**: Die Animationsgeschwindigkeit MUSS als positiver Sprite-Frames-pro-Sekunde-Wert in der zentralen Config änderbar sein und ausschließlich den Framewechsel beeinflussen.
- **FR-016**: Während der Ruhephase MUST sich der sichtbare Wurm unterhalb der StaminaBar proportional zur verstrichenen Ruhezeit von deren linker zur rechter Begrenzung bewegen; bei Ablauf MUSS er das rechte Ende erreicht haben. Diese Bewegung MUSS unabhängig vom Sprite-Framewechsel sein.
- **FR-017**: Außerhalb einer aktiven Ruhephase MUST der WormTimer einschließlich seines sichtbaren Wurms ausgeblendet sein.

### Key Entities

- **Wave Rest Phase**: Die zeitlich begrenzte Vorbereitungsphase zwischen zwei Waves mit einer über `WAVE_REST_DURATION` bestimmten Dauer, standardmäßig 10 Sekunden.
- **Wave Countdown**: Der während der aktiven Ruhephase sichtbare Fortschritt des WormTimers.
- **Wave Transition**: Der einmalige Übergang von der abgeschlossenen Wave zur nächsten Wave bei Ablauf des Countdowns.
- **Fishing Attempt**: Der bestehende Angelversuch, der ausschließlich während einer aktiven Wave-Ruhephase gestartet und fortgesetzt werden kann.
- **WormTimer Animation**: Die während der Ruhephase sichtbare, aus `WormTimer.png` geladene Sprite-Animation mit konfigurierbarer Geschwindigkeit in Sprite-Frames pro Sekunde und einer positionsabhängigen Bewegung unterhalb der StaminaBar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 20 abgeschlossenen Waves startet jedes Mal innerhalb eines Simulationsschritts die konfigurierte Ruhephase mit sichtbarem WormTimer; bei Standardkonfiguration beträgt sie 10 Sekunden.
- **SC-002**: In 20 kontrollierten Countdown-Tests bewegt sich der WormTimer monoton von links nach rechts und erreicht bei Ablauf das rechte Ende; mit Standardkonfiguration beträgt die Dauer 10 Sekunden.
- **SC-003**: In 20 Interaktionstests während der Ruhephase startet im Fishing Pond ein Angelversuch und der Countdown läuft weiter.
- **SC-004**: In 20 Übergangstests startet bei null genau eine nächste Wave; kein Test erzeugt einen doppelten Übergang.
- **SC-005**: In 20 erfolgreichen Angelversuchen während der Ruhephase wird die definierte Stamina-Belohnung vergeben; bei Ablauf der Ruhephase erhält ein gleichzeitig abgeschlossener Versuch keine Belohnung.
- **SC-006**: Mindestens 90 % der Testspieler können ohne Erklärung erkennen, dass eine Ruhephase aktiv ist und wie viel Zeit bis zur nächsten Wave verbleibt.
- **SC-007**: Alle bestehenden Wave-, Dokument-, Fishing-, Stamina-, Game-Over- und Restart-Tests bleiben nach dem Countdown-Feature erfolgreich.
- **SC-008**: Bei mindestens zwei gültigen Animationsgeschwindigkeiten zeigt der WormTimer die Sprite-Frames mit der jeweils konfigurierten Rate, ohne den Ablauf der Ruhephase oder den Wave-Übergang zu verändern.
- **SC-009**: In kontrollierten Ruhephasen erreicht der WormTimer am Ende unabhängig von der konfigurierten Dauer und Animationsgeschwindigkeit das rechte Ende der StaminaBar; während aktiver Waves ist er nicht sichtbar.

## Assumptions

- Die Ruhephase beginnt unmittelbar nach dem erfolgreichen Abschluss einer Wave und verwendet `WAVE_REST_DURATION`, dessen Standardwert 10 Sekunden beträgt.
- Die erste Wave beginnt direkt im aktiven Spielzustand und benötigt keine Ruhephasen-Anzeige.
- Die bestehende Fishing-Pond-Interaktion und `E`-Steuerung werden ausschließlich während der Ruhephase verwendet; während einer aktiven Wave außerhalb der Ruhephase blockiert der Workflow den Angelstart.
- Die Ruhephase pausiert nicht durch Bewegung, Angeln, UI-Anzeige oder andere Spieleraktionen.
- Ein während der Ruhephase aktiver Angelversuch wird bei Ablauf ohne Belohnung beendet; der Wave-Übergang bei null hat Vorrang vor jedem gleichzeitig aufgelösten Angelzustand.
- `WormTimer.png` besteht aus sieben horizontal angeordneten 64×32-Sprite-Frames, die während der Ruhephase fortlaufend wiederholt werden.
- Die bestehende Wave-Logik bestimmt weiterhin die Civil-Servant-Anzahl, Dokumentensequenzen und den Zustand der nächsten Wave.
- Die WormTimer-Animationsgeschwindigkeit wird als Sprite-Frames pro Sekunde in der zentralen Config geführt; sie beeinflusst ausschließlich den visuellen Framewechsel.
- Die WormTimer-Position wird aus dem Fortschritt der Ruhephase berechnet und bewegt sich unterhalb der StaminaBar von links nach rechts; die Sprite-Animationsgeschwindigkeit beeinflusst diese Position nicht.
