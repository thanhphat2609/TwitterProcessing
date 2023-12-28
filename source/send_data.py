import asyncio
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.identity.aio import DefaultAzureCredential
import json
import time
import csv

EVENT_HUB_CONNECTION_STR = "Endpoint=sb://eventhubtwitter.servicebus.windows.net/;SharedAccessKeyName=stream_data;SharedAccessKey=vOrwNJIxCxnjScjVVars9lq6RCq2MbpkP+AEhBDV0QQ=;EntityPath=eventhubjob"  ##fill in with the connection string from EventHub
EVENT_HUB_NAME = "eventhubjob"  ## fill in with the EventHub instance name

credential = DefaultAzureCredential()

async def read_data_from_csv(file_path):
    with open(file_path, newline='', encoding='cp850') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield [row]

async def run():
    # Create a producer client to send messages to the event hub.
    # Specify a connection string to your event hubs namespace and
    # the event hub name.
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENT_HUB_NAME
    )
    
    # Replace 'path/to/your/file.csv' with the actual path to your CSV file.
    csv_file_path = '../dataset/Streaming_Data.csv'
    
    async with producer:
        # Read data from CSV file.
        async for batch_rows in read_data_from_csv(csv_file_path):
            for row in batch_rows:
                # Adjust the column names based on your CSV structure.
                d = {
                    "Tweet": row["Tweet"],
                    "polarity": row["polarity"],
                    "subjectivity": row["subjectivity"],
                    "Sentiment": row["Sentiment"]
                }
                # Create a new batch for each row.
                event_data_batch = await producer.create_batch()
                # Add the event to the batch.
                event_data_batch.add(EventData(json.dumps(d)))

                # Send the batch of events to the event hub.
                await producer.send_batch(event_data_batch)
                time.sleep(2)
                print(d)

    # Close credential when no longer needed.
    # await credential.close()

# asyncio.run(run())
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
