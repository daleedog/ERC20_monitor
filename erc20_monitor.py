from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from web3 import Web3
import discord
import config

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(config.INFURA_URL))

# Initialize Discord client
discord_client = discord.Client(intents=discord.Intents.default())


# Task 1: Listen for ERC20 events
def listen_erc20_event():
    current_block = web3.eth.block_number
    from_block = current_block - 100  # Look back 100 blocks
    event_filter = web3.eth.filter({
        'fromBlock': from_block,
        'toBlock': 'latest',
        'address': Web3.to_checksum_address(config.ERC20_CONTRACT_ADDRESS),
        'topics': [config.TARGET_EVENT_SIGNATURE]
    })
    events = event_filter.get_all_entries()  # Get all ERC20 transfer events
    return events


# Task 2: Process and check for large transfers
def big_amount_transfer(**context):
    events = context['ti'].xcom_pull(task_ids='listen_erc20_event')
    for event in events:
        if event['args']['value'] > 1000 * (10 ** 18):  # Checking if the transfer amount is large
            message = f"Large transfer detected: From {event['args']['from']} to {event['args']['to']}, amount: {event['args']['value'] / (10 ** 18)} tokens"
            return message
    return None


# Task 3: Send a message to Discord
def send_discord_message(**context):
    message = context['ti'].xcom_pull(task_ids='process_event')
    if message:
        async def send_message():
            channel = discord_client.get_channel(config.CHANNEL_ID)
            await channel.send(message)

        discord_client.loop.create_task(send_message())


# Task 4: Anomaly detection - Check if any account is making too many transfers
def check_transfer_frequency(**context):
    current_block = web3.eth.block_number
    window_blocks = 100  # Define the size of the time window in blocks
    frequency_threshold = 10  # Define the maximum allowed transactions in the time window

    # Get events from the previous tasks
    events = context['ti'].xcom_pull(task_ids='listen_erc20_event')

    # Dictionary to track the number of transfers per account
    account_transfers = {}

    for event in events:
        from_account = event['args']['from']
        if event['blockNumber'] > current_block - window_blocks:
            if from_account not in account_transfers:
                account_transfers[from_account] = 0
            account_transfers[from_account] += 1

    # Check if any account exceeds the frequency threshold
    for account, count in account_transfers.items():
        if count > frequency_threshold:
            message = (f"Alert: Account {account} made {count} transfers in the last {window_blocks} blocks, "
                       "possible abnormal activity!")
            return message

    return None


# DAG definition
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 3),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
}

dag = DAG(
    'erc20_monitor',
    default_args=default_args,
    description='ERC20 Transfer Event Monitor with Anomaly Detection',
    schedule_interval=timedelta(seconds=3),  # Execute every 3 seconds
)

# Define individual tasks
t1 = PythonOperator(
    task_id='listen_erc20_event',
    python_callable=listen_erc20_event,
    dag=dag,
)

t2 = PythonOperator(
    task_id='process_event',
    python_callable=big_amount_transfer,
    provide_context=True,
    dag=dag,
)

t3 = PythonOperator(
    task_id='send_discord_message',
    python_callable=send_discord_message,
    provide_context=True,
    dag=dag,
)

t4 = PythonOperator(
    task_id='check_transfer_frequency',
    python_callable=check_transfer_frequency,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
t1 >> t2 >> t3
t1 >> t4 >> t3
