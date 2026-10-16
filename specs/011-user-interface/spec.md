# Feature Specification: User Interface Overlay Refresh

**Feature Branch**: `011-user-interface`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Die Fishpond- und Documents-Overlays entfernen, den InteractionButton bei möglichen Aktionen anzeigen, die Debug-Anzeige durch die StaminaBar ersetzen und bei GameOver GameOver.png anzeigen."

## Clarifications

### Session 2026-10-16

- Q: Soll das bestehende Fishing-Mini-Game und der konkrete Ablauf zur Stamina-Wiederherstellung unverändert erhalten bleiben? → A: Ja. Das Fishing-Mini-Game bleibt vollständig erhalten: während der Ruhephase im Fishing Pond auswerfen, auf den Biss warten, innerhalb des Bissfensters reagieren, das Catching-Minispiel abschließen und die bestehende Stamina-Belohnung erhalten. Feature 011 ändert daran und an den dafür nötigen Fishing-Overlays nichts.
- Q: Soll Stamina ausschließlich nach einem erfolgreichen Fischfang wiederhergestellt werden? → A: Ja. Das Betreten oder Verweilen im Fishing Pond, ein verpasster Biss und ein entkommener Fisch stellen keine Stamina wieder her; nur ein erfolgreich abgeschlossenes Catching-Minispiel gewährt die bestehende Stamina-Belohnung.
- Q: Soll die StaminaBar einen eigenen konfigurierbaren Scale-Faktor erhalten? → A: Ja. Ein positiver Scale-Wert in der Config soll standardmäßig `1.0` betragen und ausschließlich die gerenderte Größe der StaminaBar verändern; der Faktor wird zusätzlich zum bestehenden Zoom angewendet und darf Gameplay oder andere UI-Elemente nicht verändern.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Klare Interaktionshinweise (Priority: P1)

Als Spieler möchte ich nur dann einen sichtbaren Interaktionshinweis erhalten, wenn ich tatsächlich eine Aktion ausführen kann, damit ich ohne Debug-Texte erkenne, wann die Interaktionstaste relevant ist.

**Why this priority**: Der Hinweis ersetzt die bisherige textlastige Debug-Anzeige und macht die wichtigsten Aktionen unmittelbar verständlich.

**Independent Test**: Das Spiel an Dokumentquelle, Civil Servants, Angelteich und in Zuständen ohne mögliche Aktion testen und jeweils prüfen, ob der Hinweis exakt dann erscheint, wenn eine bestehende Interaktion möglich ist.

**Acceptance Scenarios**:

1. **Given** der Spieler befindet sich in Reichweite einer gültigen Dokumenten- oder Übergabeaktion, **When** keine blockierende Spielsituation vorliegt, **Then** wird `InteractionButton.png` mittig im unteren Bildschirmdrittel eingeblendet.
2. **Given** der Spieler befindet sich in einer gültigen Angelaktion während der Angelmöglichkeit, **When** die Aktion ausgelöst werden kann, **Then** wird derselbe Interaktionshinweis eingeblendet.
3. **Given** der Spieler ist außerhalb aller gültigen Interaktionsbereiche oder eine Aktion ist durch Spielregeln blockiert, **When** das Spiel läuft, **Then** wird kein Interaktionshinweis angezeigt.
4. **Given** der Interaktionshinweis wird angezeigt, **When** der Spieler sich aus dem gültigen Bereich bewegt oder die Aktion nicht mehr möglich ist, **Then** verschwindet der Hinweis ohne Verzögerung aus der nächsten Darstellung.

### User Story 2 - Kompakte und verständliche Ausdaueranzeige (Priority: P1)

Als Spieler möchte ich meine verbleibende Ausdauer oben links als klare Balkenanzeige sehen, damit ich rechtzeitig erkenne, wann Bürokratie oder andere Aktionen zum GameOver führen können.

**Why this priority**: Ausdauer ist eine zentrale Überlebensressource; die neue Anzeige muss die bisherige große Debug-Anzeige vollständig ersetzen.

**Independent Test**: Eine Spielsitzung mit voller Ausdauer starten, Ausdauer schrittweise verbrauchen und die Anzeige bei mindestens 75%, 50%, 25%, 10% und 0% prüfen.

**Acceptance Scenarios**:

1. **Given** das Spiel läuft mit voller Ausdauer, **When** die UI dargestellt wird, **Then** erscheint `StaminaBar.png` oben links mit dem langen oberen Balken als Rahmen und dem unteren Balken als hinterlegter Füllfläche in Grün.
2. **Given** die Ausdauer liegt unter 50% und mindestens bei 10%, **When** die UI dargestellt wird, **Then** wird die Füllung proportional nach links verkürzt und gelb angezeigt.
3. **Given** die Ausdauer liegt unter 10%, **When** die UI dargestellt wird, **Then** wird die Füllung proportional weiter verkürzt und rot angezeigt.
4. **Given** die Ausdauer verändert sich, **When** ein neuer Frame dargestellt wird, **Then** entspricht die Füllbreite dem aktuellen Verhältnis von Ausdauer zu Maximum und bleibt innerhalb des Balkenrahmens.
5. **Given** die Ausdauer ist 0 oder das Spiel ist im GameOver-Zustand, **When** die UI dargestellt wird, **Then** bleibt die Ausdaueranzeige gültig begrenzt und die GameOver-Darstellung hat visuelle Priorität.
6. **Given** der konfigurierbare Scale-Faktor der StaminaBar wird auf einen anderen positiven Wert gesetzt, **When** die UI dargestellt wird, **Then** ändert sich nur die gerenderte Größe der StaminaBar proportional, während Position, Gameplay, Zoomverhalten der übrigen UI und andere UI-Elemente unverändert bleiben.

### User Story 3 - Verständliche GameOver-Darstellung (Priority: P1)

Als Spieler möchte ich bei erschöpfter Ausdauer eine eindeutige GameOver-Grafik in der Bildschirmmitte sehen, damit der Zustand sofort verständlich ist und nicht von Debug-Texten überlagert wird.

**Why this priority**: Das Ende der Spielsitzung ist ein wichtiger Zustand und braucht ein klares, thematisch passendes Feedback.

**Independent Test**: Eine Spielsitzung bis auf 0 Ausdauer bringen und prüfen, ob `GameOver.png` zentriert, vollständig und ohne konkurrierendes Debug-Fenster erscheint; anschließend den bestehenden Neustart testen.

**Acceptance Scenarios**:

1. **Given** die Ausdauer erreicht 0, **When** der GameOver-Zustand aktiv wird, **Then** wird `GameOver.png` mittig im Bildschirm angezeigt.
2. **Given** die GameOver-Grafik wird angezeigt, **When** das Fenster eine andere Größe hat, **Then** bleibt die Grafik zentriert, seitenverhältnistreu und vollständig innerhalb der sichtbaren Fläche.
3. **Given** GameOver ist aktiv, **When** der Spieler den bestehenden Neustart ausführt, **Then** verschwindet die GameOver-Grafik mit dem alten Zustand und die normale HUD-Darstellung wird für die neue Spielsitzung wiederhergestellt.

### Edge Cases

- Die bisherigen sichtbaren `FISHING POND`- und `DOCUMENTS`-Beschriftungs-/Flächen-Overlays dürfen nicht mehr erscheinen; die Weltobjekte und ihre Gameplay-Funktionen bleiben erhalten.
- Die Interaktionsgrafik darf nicht erscheinen, wenn ein Dokument getragen wird und die aktuell mögliche Aktion durch die bestehende Workflow-Regel blockiert ist.
- Die Interaktionsgrafik darf nicht dauerhaft sichtbar bleiben, nachdem der Spieler den Bereich verlässt.
- Die Ausdauerfüllung darf nie über den Rahmen hinauslaufen oder eine negative Breite erhalten.
- Genau 50% Ausdauer gehört zum grünen Bereich; genau 10% gehört zum gelben Bereich. Erst Werte unter diesen Grenzen wechseln zu Gelb beziehungsweise Rot.
- Sehr kleine Fenster müssen alle neuen UI-Elemente entweder vollständig innerhalb der Fläche darstellen oder kontrolliert auf eine passende kleinere Darstellung begrenzen.
- Der positive Scale-Faktor der StaminaBar darf keine anderen UI-Elemente oder Gameplay-Werte skalieren; bei kleinen Fenstern muss die resultierende Bar weiterhin kontrolliert in die sichtbare Fläche passen.
- Die Darstellung darf nicht von der Farbe allein abhängen; der GameOver-Zustand und die bestehende Zustandslogik bleiben eindeutig erkennbar.
- Das Fishing-Mini-Game darf durch das Entfernen des Fishpond-Overlays nicht übersprungen, vereinfacht, automatisch erfolgreich oder in seinem bestehenden Ablauf beziehungsweise seiner Stamina-Belohnung verändert werden.
- Das Betreten oder Verweilen im Fishing Pond darf allein keine Stamina wiederherstellen; auch ein verpasster Biss oder ein entkommener Fisch darf keine Stamina-Belohnung auslösen. Stamina wird ausschließlich nach einem erfolgreichen Fang wiederhergestellt.
- Die Darstellung muss mit der bestehenden Zoomstufe aus Feature 010 gemeinsam funktionieren.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Das Spiel MUST die sichtbaren Fishpond- und Documents-Overlays entfernen, ohne die zugrunde liegenden Weltobjekte, Interaktionsbereiche oder Gameplay-Regeln zu entfernen.
- **FR-002**: Das Spiel MUST `InteractionButton.png` aus dem UserInterface-Assetbereich anzeigen, sobald mindestens eine bestehende Spieleraktion aktuell ausführbar ist.
- **FR-003**: Das Spiel MUST den Interaktionshinweis ausblenden, sobald keine bestehende Aktion ausführbar ist oder eine Aktion durch den aktuellen Spielzustand blockiert wird.
- **FR-004**: Der Interaktionshinweis MUST horizontal zentriert im unteren Bildschirmdrittel erscheinen und darf keine Weltposition verändern.
- **FR-005**: Das Spiel MUST die bisherige große Debug-Anzeige in der linken oberen Ecke durch die StaminaBar-Anzeige ersetzen.
- **FR-006**: Die StaminaBar-Anzeige MUST `StaminaBar.png` als Quelle mit den bekannten Abmessungen 320×64 verwenden.
- **FR-007**: Die StaminaBar MUST den langen Balken der oberen Sprite-Zeile als Rahmen und den unteren Balken als hinterlegte Füllfläche verwenden.
- **FR-008**: Bei einem Ausdauerverhältnis von 50% bis 100% MUST die Füllung grün erscheinen.
- **FR-009**: Bei einem Ausdauerverhältnis von mindestens 10% und unter 50% MUST die Füllung proportional zum aktuellen Ausdauerverhältnis verkürzt und gelb dargestellt werden.
- **FR-010**: Bei einem Ausdauerverhältnis unter 10% MUST die Füllung proportional zum aktuellen Ausdauerverhältnis verkürzt und rot dargestellt werden.
- **FR-011**: Die Füllbreite MUST auf den Bereich von leer bis vollständig gefüllt begrenzt bleiben und darf den Rahmen nicht überdecken.
- **FR-012**: Die StaminaBar MUST oben links mit einem sicheren Abstand zu den Fensterrändern dargestellt werden.
- **FR-013**: Das Spiel MUST bei aktivem GameOver `GameOver.png` mittig im Bildschirm anzeigen.
- **FR-014**: Die GameOver-Grafik MUST innerhalb der sichtbaren Fläche bleiben, ihr Seitenverhältnis bewahren und bei unterschiedlichen Fenstergrößen zentriert bleiben.
- **FR-015**: Bei aktivem GameOver MUST die GameOver-Grafik die visuelle Priorität gegenüber der normalen Gameplay-HUD erhalten, ohne den bestehenden Neustart zu deaktivieren.
- **FR-016**: Alle neuen UI-Grafiken MUST gemeinsam mit der bestehenden Zoomdarstellung aus Feature 010 konsistent skaliert werden.
- **FR-017**: Die neue UI MUST den bestehenden Spielfluss, die Zustandsübergänge, den Ausdauerverbrauch, Fishing, Dokumentenworkflow und Neustartlogik unverändert lassen. Das umfasst ausdrücklich das Fishing-Mini-Game während der Wellenruhe mit Auswerfen, Bisswartezeit, Bissfenster, Catching-Minispiel und der bestehenden Stamina-Belohnung. Eine Stamina-Wiederherstellung MUST ausschließlich nach einem erfolgreichen Fang erfolgen; bloßes Verweilen im Fishing Pond, ein verpasster Biss oder ein entkommener Fisch dürfen keine Wiederherstellung auslösen.
- **FR-018**: Die UI MUST bei kleinen und veränderten Fenstergrößen ohne Absturz, ungerenderte Flächen oder abgeschnittene zentrale Hinweise funktionieren.
- **FR-019**: Die StaminaBar MUST einen eigenen positiven Scale-Faktor aus der zentralen Config verwenden, standardmäßig `1.0`; dieser Faktor MUST ausschließlich die gerenderte Größe der StaminaBar beeinflussen und zusätzlich zur bestehenden Feature-010-Zoomdarstellung angewendet werden.

### Key Entities

- **Interaktionshinweis**: Sichtbarer Zustand der `InteractionButton.png`, der an die bestehende Ausführbarkeit einer Spieleraktion gebunden ist.
- **StaminaBar-Anzeige**: Zusammengesetzte Anzeige aus Rahmen, Füllfläche, Füllbreite, Zustandsfarbe und eigenem Config-Scale-Faktor auf Basis des aktuellen Ausdauerverhältnisses.
- **GameOver-Anzeige**: Zentrierte Darstellung von `GameOver.png`, die während des bestehenden GameOver-Zustands die normale HUD-Darstellung überlagert.
- **UI-Sichtbarkeitszustand**: Die für einen Frame berechnete Information, ob Interaktionshinweis, StaminaBar und GameOver-Anzeige sichtbar sind.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In einem Testlauf mit mindestens 10 gültigen und 10 ungültigen Interaktionssituationen ist der Interaktionshinweis in 100% der gültigen Situationen sichtbar und in 100% der ungültigen Situationen verborgen.
- **SC-002**: Die sichtbaren Fishpond- und Documents-Overlays erscheinen in keinem der bestehenden Start-, Bewegungs-, Fishing- oder Dokumentenworkflow-Szenarien mehr.
- **SC-003**: Die StaminaBar zeigt bei 100%, 50%, 25%, 10% und 0% jeweils eine innerhalb des Rahmens liegende Füllung mit der spezifizierten Farbe.
- **SC-004**: Kein UI-Element ragt bei den Referenzfenstergrößen 960×640, 800×600 und 1280×720 aus der sichtbaren Fläche heraus.
- **SC-005**: GameOver.png erscheint nach Erschöpfung innerhalb eines Toleranzbereichs von 2% der Fensterbreite und -höhe um die Bildschirmmitte.
- **SC-006**: Alle bestehenden automatisierten Gameplay- und UI-Tests bleiben erfolgreich, und Dokumente, der vollständige Fishing-Ablauf inklusive bestehender Stamina-Wiederherstellung, Ausdauer, Wellenwechsel und Neustart funktionieren weiterhin.
- **SC-007**: Die UI-Anpassung benötigt keine Änderung an Weltkoordinaten, Spawnpositionen oder Gameplay-Balancingwerten.
- **SC-008**: Bei mindestens zwei positiven StaminaBar-Scale-Werten, darunter `0.5` und `1.5`, verändert sich die gerenderte Bar-Größe proportional, ohne dass Position, andere UI-Elemente, Weltkoordinaten oder Gameplay-Werte verändert werden.

## Assumptions

- `InteractionButton.png` wird als E-Tasten-Hinweis für alle bestehenden Aktionen verwendet, die aktuell über die Interaktionstaste ausgelöst werden.
- Die Interaktionsanzeige ist sichtbar, sobald eine Aktion unmittelbar ausführbar ist; während eines blockierenden Warte- oder Übergabezustands bleibt sie verborgen, außer die bestehende Logik erlaubt ausdrücklich eine Eingabe.
- Die obere Zeile der StaminaBar ist der Rahmen und die untere Zeile die Füllgrafik; die Füllgrafik wird für Grün, Gelb und Rot entsprechend eingefärbt.
- Die Füllung ist linksbündig im Rahmen verankert und ihre Breite entspricht dem aktuellen Ausdauerverhältnis.
- Der aktuelle Zoom-Multiplikator aus Feature 010 gilt für die gesamte UI-Präsentation; zusätzlich steuert ein eigener positiver StaminaBar-Scale-Faktor mit Standardwert `1.0` nur die Größe der StaminaBar. Die Assets bleiben austauschbare Quelldateien.
- Für GameOver wird die Grafik proportional so angepasst, dass sie mit einem sicheren Rand vollständig in die aktuelle sichtbare Fläche passt.
- Die bestehende Neustartfunktion bleibt erhalten; diese Feature-Spec ersetzt nur die visuelle Darstellung.
- Der bestehende Fishing-Ablauf bleibt maßgeblich: Fishing ist während der Wellenruhe im Fishing Pond möglich, erfordert Auswerfen, Bisswartezeit, Reaktion im Bissfenster und das Catching-Minispiel; ausschließlich ein erfolgreicher Fang gewährt die bestehende Stamina-Belohnung, nicht das bloße Verweilen im Pond oder ein Fehlversuch.
- Weitere vorhandene UI-Assets wie SpeechBubble oder FishingMeter sind nicht Teil dieser Änderung, sofern sie nicht bereits durch die bestehenden Fishing-Szenarien benötigt werden.
