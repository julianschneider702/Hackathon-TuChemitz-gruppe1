# VitalCheck

Ein KI-gestützter Assistent für die persönliche Gesundheitsvorsorge – entstanden als Team-Hackathon-Projekt.

VitalCheck führt Nutzer anhand ihres individuellen Gesundheitsprofils (Vorerkrankungen, Familienanamnese, Lebensstil) durch einen persönlichen Vorsorge-Check und gibt über einen Chat personalisierte Empfehlungen.

## Features

- **Chat-Assistent** mit personalisierten Empfehlungen auf Basis des Nutzerprofils
- **Impfpass-Übersicht** inkl. CSV-Import zum schnellen Einpflegen bestehender Daten
- **Vorsorge-Tracker** mit anstehenden Terminen und Erinnerungen
- **VitalScore** als kompakter Gesundheitsüberblick

## Architektur

Das Frontend ist eine eigenständige HTML/CSS/JS-App im Handy-Rahmen-Design. Die eigentliche Logik läuft über drei orchestrierte **n8n-Workflows**, die per Webhook angebunden sind:

1. **Start-Workflow** – initiiert die Session und liefert die erste Chat-Nachricht
2. **Chat-Workflow** – verarbeitet jede Nutzernachricht und liefert die KI-Antwort
3. **Abschluss-Workflow** – erstellt die finale Auswertung/Zusammenfassung

Eine Session-ID hält den Gesprächskontext über alle drei Workflow-Aufrufe hinweg konsistent. Das Nutzerprofil wird als strukturierter JSON-Kontext übergeben, damit die Antworten personalisiert ausfallen. Die Antwortverarbeitung ist bewusst robust gehalten, sodass unterschiedliche Rückgabeformate (JSON-Objekt, Array, Klartext) zuverlässig geparst werden.

## Tech-Stack

- Frontend: HTML, CSS, JavaScript
- Automatisierung/Backend: n8n (Webhook-basiert)
- Datenimport: CSV-Parser für Impfpass- und Vorsorgedaten

## Hinweis

Dies ist ein Hackathon-Prototyp. Die n8n-Workflows laufen auf einer externen Instanz und sind nicht Teil dieses Repos.
