import grpc
import image_pb2 as image_pb2
import image_pb2_grpc as image_pb2_grpc
from typing import Any

async def call_image_service(owner_name: str, image_data: Any) -> dict:
    # Kết nối với Service B qua gRPC
    channel = grpc.insecure_channel("service_b:50051")  # Đảm bảo rằng Service B đang chạy trên cổng này
    stub = image_pb2_grpc.ImageServiceStub(channel)
    
    # Chuyển đổi ảnh và owner_name vào request gRPC
    request = image_pb2.ImageRequest(owner_name=owner_name, image_data=image_data.read())
    
    try:
        response = stub.ProcessImage(request)
        return {
            "success": response.success,
            "flipped_image": response.flipped_image,
            "error_message": response.error_message
        }
    except grpc.RpcError as e:
        return {"success": False, "error_message": str(e)}
