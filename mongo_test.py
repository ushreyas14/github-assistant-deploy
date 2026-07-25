import asyncio

from mongodb import chunks_collection

async def test():

    await chunks_collection.insert_one(
        {
            "_id": "test_chunk",
            "symbol_name": "test",
            "content": "hello world"
        }
    )

    print("Inserted")

asyncio.run(test())