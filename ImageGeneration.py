import bpy
import sys
import subprocess
import ensurepip

#install package
#packages_path = "C:\\Users\\<Username>\\AppData\\Roaming\\Python\\Python39\\Scripts" + "\\..\\site-packages" # the path you see in console
#ensurepip.bootstrap()
#pybin = sys.executable
#subprocess.check_call([pybin, '-m', 'pip', 'install', 'replicate'])

# Save a render
scene = bpy.data.scenes['Scene']
render = scene.render
border_res_x = render.resolution_x * 0.5
border_res_y = render.resolution_y * 0.5
render.resolution_x = round(border_res_x) 
render.resolution_y = round(border_res_y)
path = bpy.data.filepath[:len(bpy.data.filepath) - bpy.data.filepath[::-1].find('\\')] + '\\ImageGeneration\\' + 'referenceImage.jpeg'
bpy.context.scene.render.image_settings.file_format='JPEG'
bpy.context.scene.render.filepath = path
bpy.ops.render.render(use_viewport = True, write_still=True)

# Upload it to s3
import boto3
import uuid
from botocore.exceptions import ClientError
s3_client = boto3.client('s3', 
                      aws_access_key_id='AKIAQC45DLWIRZZW73MN', 
                      aws_secret_access_key='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', 
                      region_name='us-east-2'
                      )
key = uuid.uuid4().hex
bucket = 'raccoonplugin'
try:
    response = s3_client.upload_file(path, bucket, key)
except ClientError as e:
    print(e)
    
# Get presigned URL
try:
    response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket,
                                                            'Key': key},
                                                    ExpiresIn=120)
    print(response)
except ClientError as e:
    print(e)

# Create AI image
import replicate
import os
os.environ["REPLICATE_API_TOKEN"] = "eee4b2d52508ae08f1981c09a618bbb606595d68"
model = replicate.models.get("stability-ai/stable-diffusion")
version = model.versions.get("8abccf52e7cba9f6e82317253f4a3549082e966db5584e92c808ece132037776")
output = version.predict(prompt="concept art technical drawing syd mead", init_image=response, height=512, width=512,
prompt_strength=0.65,num_outputs = 1, num_inference_steps = 50, guidance_scale = 10, seed = 5415)