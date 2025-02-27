import sys
import os
from fastapi import FastAPI, HTTPException, File, Form, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import grpc
import boundary_test_and_image.image_pb2 as image_pb2
import boundary_test_and_image.image_pb2_grpc as image_pb2_grpc
from io import BytesIO
from typing import Union
from boundary_test_and_image.image_video_detect import Detection
from boundary_test_and_image.param_constraints import ParamConstraints
from boundary_test_and_image.boundary_test_owner_name import boundary_test_owner_name 
import boundary_test_and_image.EXCEPTION_MESSAGE as msg

app = FastAPI()
detection = Detection()
cp = ParamConstraints()
channel = grpc.insecure_channel('192.168.1.74:50051')  # Địa chỉ IP của máy chạy Service B
stub = image_pb2_grpc.ImageServiceStub(channel)

@app.post("/process-image/")
async def process_image(owner_name: str = Form(...), input: UploadFile = File(...)):
    # Sanitize inputs
    image_data = await input.read()
    if not owner_name:
        return JSONResponse(content={"message": msg.OWNER_NAME_NOT_NULL}, status_code=400)
    if input.size==0:
        return JSONResponse(content={"message": msg.IMAGE_NOT_NULL}, status_code=400)
    boundary_test_result = boundary_test_owner_name(owner_name, min_length=1, max_length=50)
    if boundary_test_result:  # Nếu có lỗi, trả về JSON response lỗi
        return boundary_test_result
    input_file = BytesIO(image_data)  # Chuyển đổi dữ liệu thành đối tượng file-like

    # Check if the file is a valid image
    if not detection.isImage(input_file):
        return JSONResponse(content={"message": msg.INVALID_IMAGE_ERROR}, status_code=400)

    # Check the file size using get_size method
    file_size = len(image_data)  # File size in bytes
    constraints = cp.get_constraints_by_name_type('image', 'img')  # Get the constraints for image

    # Check if the file size is within the acceptable limits
    if file_size < int(constraints['param_limit_min']) or file_size > int(constraints['param_limit_max'])* 1024 * 1024:
        error_message = msg.FILE_SIZE_ERROR.format(min_size=constraints['param_limit_min'], max_size=constraints['param_limit_max'])
        return JSONResponse(content={"message": error_message}, status_code=400)

    try:
        # Send image and owner_name to Service B
        request = image_pb2.ImageRequest(image_data=image_data, owner_name=owner_name)
        response = stub.ProcessImage(request)
        
        if response.success:
            # Return the flipped image as a streaming response
            return StreamingResponse(BytesIO(response.flipped_image), media_type="image/png")
        else:
            return JSONResponse(content={"message": msg.OWNER_NAME_EXISTING}, status_code=400)
    except grpc.RpcError as e:
        return JSONResponse(content={"message":msg.GRPC_CONNECTION_ERROR}, status_code=500)
    #(DucMinh) PS C:\Users\LENOVO\Desktop\eyeQ_Tech_Task> uvicorn main:app --reload --host 0.0.0.0 --port 8000
