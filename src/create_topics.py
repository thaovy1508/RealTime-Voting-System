# create_topics.py
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def create_topics():
    admin_client = KafkaAdminClient(
        bootstrap_servers="localhost:9092"
    )
    
    topic_list = [
        NewTopic(name="votes_topic", num_partitions=1, replication_factor=1),
        NewTopic(name="party_votes_topic", num_partitions=1, replication_factor=1),
        NewTopic(name="time_trends_topic", num_partitions=1, replication_factor=1)
    ]
    
    try:
        admin_client.create_topics(topic_list)
        print("Topics created successfully!")
    except TopicAlreadyExistsError:
        print("Topics already exist!")
    except Exception as e:
        print(f"Error creating topics: {e}")
    finally:
        admin_client.close()

if __name__ == "__main__":
    create_topics()