from faker import Faker

faker = Faker()


def generate_graph_state():
    """
    Generate a random GraphState instance.
    """
    return {
        "question": faker.sentence(),  # Generate a random question
        "generation": faker.text(max_nb_chars=200),  # Simulated LLM generation text
        "web_search": faker.boolean(),  # Randomly True or False
        "documents": [
            faker.word() for _ in range(faker.random_int(min=1, max=5))
        ],  # Random list of documents
        "chat_history": [],  # Random chat history
    }
