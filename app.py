import gradio as gr
from requests.exceptions import ConnectTimeout
import time
import requests
global headers
global cancel_url
global path
path = ''
cancel_url =''
headers = {   
        'Content-Type': 'application/json',
        'Authorization': 'Token r8_Rw4lbd31DysolwMmWlgEKSA5sw1yzfT0lppJ5',
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": '**',
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PATCH"}

with gr.Blocks() as demo:
    owner = "stability-ai"
    name = "stable-diffusion"
   
    max_retries = 3
    retry_delay = 2
    for retry in range(max_retries):
       try:
          url = f'https://api.replicate.com/v1/models/{owner}/{name}'
          response = requests.get(url,  headers=headers, timeout=10)
        # Process the response
          break  # Break out of the loop if the request is successful
       except ConnectTimeout:
        if retry < max_retries - 1:
            print(f"Connection timed out. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Max retries exceeded. Unable to establish connection.")

    data = response.json()
    description =data.get("description", '')
    title = data.get("default_example",'').get("model",'')
    version = data.get("default_example",'').get("version",'')

    gr.Markdown(
    f"""
    # {title}
     {description}
    """)

    with gr.Row():
        with gr.Column():
            inputs =[]
            schema =data.get("latest_version", {}).get("openapi_schema", {}).get("components", {}).get("schemas", {})
            ordered_properties = sorted(schema.get("Input", {}).get("properties", {}).items(), key=lambda x: x[1].get("x-order", 0))
            for property_name, property_info in ordered_properties :
                if "x-order" in property_info:
                    order = int(property_info.get('x-order',''))
                    if property_info.get("type", {}) == "integer":
                        value= data.get('default_example', '').get('input','').get(property_name,0)
                        if "minimum" and "maximum" in property_info:
                            if value == 0:
                              inputs.insert(order, gr.Slider(label=property_info.get('title', ''), info=property_info.get('description',''), value=property_info.get('default', value), minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', ''), step=1))
                            else:
                              inputs.insert(order, gr.Slider(label=property_info.get('title', ''), info=property_info.get('description',''), value=value, minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', ''), step=1)) 
                        else:
                            if value == 0:
                               inputs.insert(order, gr.Number(label=property_info.get('title', ''), info=property_info.get('description',''), value=property_info.get('default', value)))
                            else:
                               inputs.insert(order, gr.Number(label=property_info.get('title', ''), info=property_info.get('description',''), value=value))
                            
                    elif property_info.get("type", {}) == "string":
                        value= data.get('default_example', '').get('input','').get(property_name,'')
                        if  property_info.get('format','') == 'uri':
                            if 'image' in property_info.get('title', '').lower():
                                if value :
                                        inputs.insert(order, gr.Image(label=property_info.get('title', ''), value=value))
                                else :
                                        inputs.insert(order, gr.Image(label=property_info.get('title', '')))
                            # elif property_info.get('title','') == 'Image Path':
                            #     inputs.insert(order, gr.Image(label=property_info.get('title', ''), value=property_info.get('default', value)))
                            else:
                                inputs.insert(order, gr.File(label=property_info.get('title', '')))
                        else:
                            if value == '':
                               inputs.insert(order, gr.Textbox(label=property_info.get('title', ''), info=property_info.get('description', ''), value=property_info.get('default', value)))
                            else:
                               inputs.insert(order, gr.Textbox(label=property_info.get('title', ''), info=property_info.get('description', ''), value=value))

                    elif property_info.get("type", {}) == "number":
                        value= data.get('default_example', '').get('input','').get(property_name, 0)
                        if "minimum" and "maximum" in property_info:
                            if value == 0:
                                inputs.insert(order, gr.Slider(label=property_info.get('title', ''), info=property_info.get('description', ''), value=property_info.get('default', value), minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', '')))
                            else:
                                inputs.insert(order, gr.Slider(label=property_info.get('title', ''), info=property_info.get('description', ''), value=value, minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', '')))
                        else:
                            if value == 0:
                              inputs.insert(order, gr.Number(label=property_info.get('title', ''), info=property_info.get('description', ''), value=property_info.get('default', value)))
                            else:
                              inputs.insert(order, gr.Number(label=property_info.get('title', ''), info=property_info.get('description', ''), value=value)) 
                    elif property_info.get("type", {}) == "boolean":
                        value= data.get('default_example', '').get('input','').get(property_name,'')
                        if value == '':
                           inputs.insert(order, gr.Checkbox(label=property_info.get('title', ''), info=property_info.get('description', ''), value=property_info.get('default', value)))
                        else:
                            inputs.insert(order, gr.Checkbox(label=property_info.get('title', ''), info=property_info.get('description', ''), value=value))
                    else:
                        value= data.get('default_example', '').get('input','').get(property_name,'')
                        options=schema.get(property_name,'').get('enum',[])
                        if value == '':
                          inputs.insert(order, gr.Dropdown(label=property_name, info=property_info.get('description', ''),choices=options, value=property_info.get("default", value)))
                        else: 
                          inputs.insert(order, gr.Dropdown(label=property_name, info=property_info.get('description', ''),choices=options, value=value))  
            with gr.Row():
                cancel_btn = gr.Button("Cancel")
                run_btn = gr.Button("Run")
                 
        with gr.Column():
            
            outputs = []
            chain =''
            if schema.get("Output",{}).get("type",'') == "array":
                for item in data.get("default_example",'').get("output",[]):
                    if schema.get("Output",{}).get("items", '').get("type",'') == "string":
                        if  schema.get("Output",{}).get("items", '').get("format",'') == "uri":
                            outputs.append(gr.Image(value=item))
                        else:
                            if schema.get("Output",{}).get('x-cog-array-display','') == "concatenate":
                                chain = chain + item
                                outputs=gr.Textbox(value=chain)
                            else:
                                outputs.append(gr.Textbox(value=item))
            elif schema.get("Output",{}).get("type",'') == "object":
                if schema.get("Output",{}).get("properties",'') == "media_path":
                   outputs= gr.File()
                    # value= data.get("default_example",'').get("output", '').get("media_path",'')
                properties = schema.get("Output", {}).get("properties", {})
                if isinstance(properties, dict):
                    for key, item in properties.items():
                            if item.get('type', '') == 'string':
                                if item.get('format', '') == 'uri':
                                    outputs.append(gr.Image())

            else:
                if schema.get("Output",{}).get("type",'') == "string":
                        if  schema.get("Output",{}).get("format",'') == "uri":
                            path=(data.get("default_example",'').get("output",''))
                            print(path)
                            if '.png' in path:
                                outputs=(gr.Image(value=path))
                            else:
                                outputs=(gr.Image())
                        else:
                            outputs=(gr.Textbox(value=data.get("default_example",'').get("output",'')))
           
    
    def run_process(input1,input2,input3,input4,input5,input6,input7, input8, input9):
       global cancel_url
       url = 'https://api.replicate.com/v1/predictions'
       body = {
            "version": version,
            "input": {
                "prompt": input1,
                "height": input2,
                "width": input3,
                "negative_prompt": input4,
                "num_outputs": input5,
                "num_inference_steps": input6,
                "guidance_scale": input7,
                "scheduler": input8,
                "seed": input9,
            }
            }
       response = requests.post(url, headers=headers, json=body)
       print(response.status_code)
       if response.status_code == 201:
            response_data = response.json()
            get_url = response_data.get('urls','').get('get','')
            cancel_url = response_data.get('urls','').get('cancel','')
            print(get_url)
            time.sleep(3)
            output =verify_image(get_url) 
            print(output)
            if output == '':
                  return
            else:
                  for item in output:
                   return  gr.Image(value=item)
       return gr.Image()
    
    def cancel_process(input1,input2,input3,input4,input5,input6,input7, input8, input9):
        print(cancel_url,"cancel_url")
        if cancel_url == '':
          return gr.Image(value='https://replicate.delivery/pbxt/sWeZFZou6v3CPKuoJbqX46ugPaHT1DcsWYx0srPmGrMOCPYIA/out-0.png')
         
        else :
           response = requests.get(cancel_url, headers=headers)
           return gr.Image(value='https://replicate.delivery/pbxt/sWeZFZou6v3CPKuoJbqX46ugPaHT1DcsWYx0srPmGrMOCPYIA/out-0.png')
      

    def verify_image(get_url):
     res = requests.get(get_url, headers=headers)
     if res.status_code == 200:
        res_data = res.json()
        print(res_data)
      
        output =  res_data.get('output', '')
        print(output,'111')
        if output == '':
                time.sleep(1)
                verify_image(get_url)
        else:
                print(output,'222')
                return output
     else: 
        return  ''  
    
    run_btn.click(run_process, inputs=inputs, outputs=outputs, api_name="run")
    cancel_btn.click(cancel_process, inputs=inputs, outputs=outputs, api_name="cancel")

demo.launch()


         


