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
from typing import Any
from fastapi import FastAPI, HTTPException, Form, UploadFile, Request, File, Depends
app = FastAPI()
detection = Detection()
cp = ParamConstraints()
channel = grpc.insecure_channel('192.168.1.74:50051')  # Địa chỉ IP của máy chạy Service B
stub = image_pb2_grpc.ImageServiceStub(channel)

# Dependency để kiểm tra và xác nhận dữ liệu form
async def validate_form_data(request: Request) -> Any:
    # Lấy tất cả các trường trong body request
    body_fields = await request.form()

    # Kiểm tra số lượng trường
    if len(body_fields) != 2:
        raise HTTPException(status_code=400, detail="Only two fields ('owner_name' and 'input') are allowed.")

    # Kiểm tra nếu có trường nào không phải là owner_name hoặc input
    allowed_fields = {'owner_name', 'input'}
    provided_fields = set(body_fields.keys())

    if not provided_fields.issubset(allowed_fields):
        raise HTTPException(status_code=400, detail="Invalid fields in the request. Only 'owner_name' and 'input' are allowed.")
# Kiểm tra nếu trường 'input' là file (UploadFile)
    input_file = body_fields.get('input')
    if isinstance(input_file, UploadFile):
        raise HTTPException(status_code=400, detail="'input' must be a file")
    # Kiểm tra xem có chính xác một file không
    if len(body_fields.getlist('input')) != 1:
        raise HTTPException(status_code=400, detail="Only one input")
    if len(body_fields.getlist('owner_name')) != 1:
        raise HTTPException(status_code=400, detail="Only one owner_name")
    # Kiểm tra nếu trường 'owner_name' là chuỗi (string)
    owner_name = body_fields.get('owner_name')
    if not isinstance(owner_name, str):
        raise HTTPException(status_code=400, detail="'owner_name' must be a string")
    # Trả về body_fields hợp lệ
    return body_fields

@app.post("/process-image/")
async def process_image(body_fields: Any = Depends(validate_form_data)):
    # Lấy dữ liệu từ body_fields
    owner_name = body_fields.get('owner_name')
    input_file = body_fields.get('input')

    # Sanitize inputs
    image_data = await input_file.read()
    if not owner_name:
        return JSONResponse(content={"message": msg.OWNER_NAME_NOT_NULL}, status_code=400)
    if input_file.size == 0:
        return JSONResponse(content={"message": msg.IMAGE_NOT_NULL}, status_code=400)
    
    boundary_test_result = boundary_test_owner_name(owner_name, min_length=1, max_length=50)
    if boundary_test_result:  # Nếu có lỗi, trả về JSON response lỗi
        return boundary_test_result
    
    input_file_stream = BytesIO(image_data)  # Chuyển đổi dữ liệu thành đối tượng file-like

    # Check if the file is a valid image
    if not detection.isImage(input_file_stream):
        return JSONResponse(content={"message": msg.INVALID_IMAGE_ERROR}, status_code=400)

    # Check the file size using get_size method
    file_size = len(image_data)  # File size in bytes
    constraints = cp.get_constraints_by_name_type('image', 'img')  # Get the constraints for image

    # Check if the file size is within the acceptable limits
    if file_size < int(constraints['param_limit_min']) or file_size > int(constraints['param_limit_max']) * 1024 * 1024:
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
        return JSONResponse(content={"message": msg.GRPC_CONNECTION_ERROR}, status_code=500)
