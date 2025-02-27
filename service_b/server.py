import grpc
from pymongo import errors
from concurrent import futures
import boundary_test_and_image.image_pb2 as image_pb2
import boundary_test_and_image.image_pb2_grpc as image_pb2_grpc
from pymongo import MongoClient
import io

import boundary_test_and_image.EXCEPTION_MESSAGE as msg
from PIL import Image


class ImageService(image_pb2_grpc.ImageServiceServicer):
    def __init__(self):
        try:
            # Cố gắng kết nối MongoDB
            self.client = MongoClient("mongodb://192.168.1.74:27018")
            self.db = self.client.image_db
            self.collection = self.db.owner_names
            # Kiểm tra kết nối bằng cách ping database
            self.client.admin.command('ping')
            print("MongoDB connection successful.")
        except errors.ServerSelectionTimeoutError as e:
            print(f"MongoDB connection error: {e}")
            raise Exception(msg.MONGO_CONNECTION_ERROR)
        except errors.ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            raise Exception(msg.MONGO_CONNECTION_ERROR)
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise Exception(msg.MONGO_CONNECTION_ERROR)

    def ProcessImage(self, request, context):
        owner_name = request.owner_name
        image_data = request.image_data
        
        # Check if owner_name already exists in MongoDB
        if self.collection.find_one({"owner_name": owner_name}):
            return image_pb2.ImageResponse(
                success=False,
                error_message= msg.OWNER_NAME_EXISTING
            )
        
        # Process the image (flip horizontally)
        image = Image.open(io.BytesIO(image_data))
        flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
        
        # Convert image back to bytes
        with io.BytesIO() as output:
            flipped_image.save(output, format="PNG")
            flipped_image_data = output.getvalue()
        
        # Store the owner_name in the MongoDB collection
        self.collection.insert_one({"owner_name": owner_name})

        # Return the flipped image as bytes
        return image_pb2.ImageResponse(
            success=True,
            flipped_image=flipped_image_data  # Returning image as bytes
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_pb2_grpc.add_ImageServiceServicer_to_server(ImageService(), server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    print("Service B is running on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
#(DucMinh) PS C:\Users\LENOVO\Desktop\eyeQ_Tech_Task\service_b> python .\server.py