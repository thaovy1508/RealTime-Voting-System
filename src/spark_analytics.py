# src/spark_analytics.py
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, count, sum as _sum, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

class VotingAnalytics:
    def __init__(self):
        # Create directories
        try:
            current_dir = os.getcwd()
            self.checkpoints_dir = os.path.join(current_dir, 'checkpoints')
            
            # Create checkpoint directories
            os.makedirs(os.path.join(self.checkpoints_dir, 'party_votes'), exist_ok=True)
            os.makedirs(os.path.join(self.checkpoints_dir, 'time_trends'), exist_ok=True)
            
            print(f"Current directory: {current_dir}")
            print(f"Checkpoints directory: {self.checkpoints_dir}")
            print("Checkpoint directories created successfully")
        except Exception as e:
            print(f"Error creating directories: {e}")
            raise e

        self.spark = (SparkSession.builder
                     .appName("VotingAnalytics")
                     .master("local[*]")
                     .config("spark.driver.host", "localhost")
                     .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")
                     .config("spark.sql.shuffle.partitions", "2")
                     .getOrCreate())

        self.spark.sparkContext.setLogLevel("ERROR")

        self.vote_schema = StructType([
            StructField("vote_id", StringType(), True),
            StructField("voter_id", StringType(), True),
            StructField("voter_name", StringType(), True),
            StructField("candidate_id", StringType(), True),
            StructField("candidate_name", StringType(), True),
            StructField("party", StringType(), True),
            StructField("voted_at", TimestampType(), True),
            StructField("vote", IntegerType(), True)
        ])

    def process_party_votes(self, df):
        party_votes = df.groupBy("party") \
            .agg(_sum("vote").alias("total_votes")) \
            .select(to_json(struct("*")).alias("value"))

        checkpoint_path = os.path.join(self.checkpoints_dir, 'party_votes')
        
        return party_votes.writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("topic", "party_votes_topic") \
            .option("checkpointLocation", checkpoint_path) \
            .outputMode("complete") \
            .trigger(processingTime='5 seconds').start()

    def process_time_trends(self, df):
        time_votes = df.withWatermark("voted_at", "1 minute") \
            .groupBy(window("voted_at", "1 minute")) \
            .agg(_sum("vote").alias("total_votes")) \
            .select(to_json(struct("*")).alias("value"))

        checkpoint_path = os.path.join(self.checkpoints_dir, 'time_trends')
        
        return time_votes.writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("topic", "time_trends_topic") \
            .option("checkpointLocation", checkpoint_path) \
            .outputMode("append") \
            .trigger(processingTime='5 seconds').start()

    def read_from_kafka(self):
        return (self.spark
                .readStream
                .format("kafka")
                .option("kafka.bootstrap.servers", "localhost:9092")
                .option("subscribe", "votes_topic")
                .option("startingOffsets", "latest")
                .load())

    def process_votes(self):
        try:
            print("Starting to process votes...")
            kafka_df = self.read_from_kafka()
            print("Connected to Kafka input stream")
            
            votes_df = (kafka_df
                    .selectExpr("CAST(value AS STRING)")
                    .select(from_json(col("value"), self.vote_schema).alias("data"))
                    .select("data.*"))
            print("Created votes DataFrame")

            query1 = self.process_party_votes(votes_df)
            print("Started party votes processing")
            
            query2 = self.process_time_trends(votes_df)
            print("Started time trends processing")
            
            print("All streams started successfully")
            query1.awaitTermination()
            query2.awaitTermination()
        
        except Exception as e:
            print(f"Error processing votes: {e}")
            import traceback
            traceback.print_exc()
            raise e

if __name__ == "__main__":
    analytics = VotingAnalytics()
    try:
        analytics.process_votes()
    except KeyboardInterrupt:
        print("\nStopping analytics...")
        analytics.spark.stop()