from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urljoin

def submitData(race_url, user_data, parameter_names):
    session = HTMLSession()
    
    forms = get_all_forms(race_url, session)
    if(len(forms) < 2):
        return "Failed to find signup form. Perhaps the event is already over?"
    else:
        form = forms[1]
        form_details = get_form_details(form)
        i = 0
        captcha_solution = get_captcha_solution(form_details);
    
        data = {}
        for input_tag in form_details["inputs"]:
            if ((input_tag["type"] == "hidden") or (input_tag["name"] == "rtec_user_comments")): 
                data[input_tag["name"]] = input_tag["value"] # Use default value
            elif input_tag["name"] == "rtec_recaptcha":
                data[input_tag["name"]] = captcha_solution
            elif input_tag["type"] == "checkbox":
                data[input_tag["name"]] = "true"
            elif input_tag["type"] != "submit": # take from user data
                value = user_data.get(parameter_names[i])
                data[input_tag["name"]] = value
                i += 1
            
        # join the url with the action (form request URL)
        race_url = urljoin(race_url, form_details["action"])

        res = session.post(race_url, data=data)
        return validate(res)

def validate(res):
    errors = ""
    soup = BeautifulSoup(res.html.html, "html.parser")
    forms = soup.find_all("form")
    if(len(forms) > 1):
        form = soup.find_all("form")[1]
        form_details = get_form_details(form)   
        for input_tag in form_details["inputs"]:
            if("aria-invalid" in input_tag.keys() and input_tag["aria-invalid"] == "true"):
                split = input_tag["name"].split("_")
                error = split[len(split) - 1]
                errors += "Invalid " + error + "\n"             
    return errors
        

def get_captcha_solution(form_details):
    for input_tag in form_details["inputs"]:
        if input_tag["name"] == "rtec_recaptcha_sum":
            return input_tag["value"]
    return 5 #Try your luck I guess if you reach here, though should really throw an exception

def get_all_forms(url, session):
    """Returns all form tags found on a web page's `url` """
    # GET request
    res = session.get(url)
    # for javascript driven website
    # res.html.render()
    soup = BeautifulSoup(res.html.html, "html.parser")
    return soup.find_all("form")  

def get_form_details(form):
    """Returns the HTML details of a form,
    including action, method and list of form controls (inputs, etc)"""
    details = {}
    # get the form action (requested URL)
    action = form.attrs.get("action").lower()
    # get the form method (POST, GET, DELETE, etc)
    # if not specified, GET is the default in HTML
    method = form.attrs.get("method", "get").lower()
    # get all form inputs
    inputs = []
    for input_tag in form.find_all("input"):
        # get type of input form control
        input_type = input_tag.attrs.get("type", "text")
        # get name attribute
        input_name = input_tag.attrs.get("name")
        # get the default value of that input tag
        input_value =input_tag.attrs.get("value", "")
        # get the validity of input
        input_invalid = input_tag.attrs.get("aria-invalid")
        # add everything to that list
        inputs.append({"type": input_type, "name": input_name, "value": input_value, "aria-invalid": input_invalid})
    # put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details
    