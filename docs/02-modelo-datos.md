Tablas propuestas:

    users: almacena información de los agentes (los que acceden al panel).

        id (PK)

        username (único)

        email (único)

        hashed_password

        is_active

        created_at

    customers: representa a los usuarios finales (los que chatean).

        id (PK)

        phone_number (único para WhatsApp) o session_id (para web)

        name (opcional, se puede pedir después)

        created_at

    conversations: cada hilo de conversación.

        id (PK)

        customer_id (FK a customers)

        status: 'bot', 'human', 'ended'

        created_at

        updated_at

    messages: cada mensaje intercambiado.

        id (PK)

        conversation_id (FK)

        sender: 'customer', 'bot', 'human'

        content (texto)

        intent_detected (opcional, para depuración)

        created_at

    settings: configuración global (prompt de IA, frases de derivación, etc.)

        id (PK)

        key (único)

        value (texto)

        description
        ___________________________________________________
        2. Diagrama de entidad - relación
    
    CUSTOMERS ||--o{ CONVERSATIONS : tiene
    CONVERSATIONS ||--o{ MESSAGES : contiene
    USERS ||--o{ MESSAGES : "responde como humano"
    SETTINGS ||--o| CONFIG : "guarda"