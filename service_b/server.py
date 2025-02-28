import grpc
from pymongo import errors
from concurrent import futures
import boundary_test_and_image.image_pb2 as image_pb2
import boundary_test_and_image.image_pb2_grpc as image_pb2_grpc
from pymongo import MongoClient
import io
from fastapi.responses import JSONResponse

import boundary_test_and_image.EXCEPTION_MESSAGE as msg
from PIL import Image


class ImageService(image_pb2_grpc.ImageServiceServicer):
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        
        try:
            # Cố gắng kết nối MongoDB
            self.client = MongoClient("mongodb://192.168.1.74:27018")  # Đảm bảo MongoClient được khởi tạo
            self.db = self.client.image_db
            self.collection = self.db.owner_names
            # Kiểm tra kết nối bằng cách ping database
            self.client.admin.command('ping')
            print("MongoDB connection successful.")
        except errors.ServerSelectionTimeoutError as e:
            return image_pb2.ImageResponse(
                success=False,
                error_message= msg.CONNECTION_ERROR
            )
        except errors.ConnectionFailure as e:
           return image_pb2.ImageResponse(
                success=False,
                error_message= msg.CONNECTION_ERROR
            )
        except Exception as e:
            return image_pb2.ImageResponse(
                success=False,
                error_message= msg.CONNECTION_ERROR
            )

    def _check_mongo_connection(self):
        """Hàm phụ để kiểm tra kết nối MongoDB trước khi xử lý bất kỳ yêu cầu nào."""
        if self.client is None or not self.client.admin.command('ping'):
            return False
        return True

    def ProcessImage(self, request, context):
        if not self._check_mongo_connection():
            # Nếu không thể kết nối MongoDB, trả về lỗi
            return image_pb2.ImageResponse(
                success=False,
                error_message=msg.CONNECTION_ERROR
            )
        
        owner_name = request.owner_name
        image_data = request.image_data
        owner_name = owner_name.strip()

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
        if '\n' in owner_name or '\t' in owner_name:
            return JSONResponse(content={"message": msg.OWNER_NAME_NO_NEWLINE_TAB_ERROR}, status_code=400)
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
