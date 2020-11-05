#############################################################
#       GovTechaThon-2020                                   #
#       Team Name: Dabhole Nishandar                        #
#       Webapp link - www.dabnish.pythonanywhere.com        #
#       Databse - Firebase                                  #
#       Backend - Python 3.8                                #
#       Frontend -Dash Framework                            #
#############################################################

##=============================================================================================================
#DEPENDENCIES - 
#======== DASH FRAMEWORK (FOR FRONTEND)===========
import dash
import dash_auth
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc 
import dash_table
from dash_extensions import Download
from dash_extensions.snippets import send_file

#======== DATA HANDLING ===========
import pandas as pd
import datetime
import numpy as np

#======== COMMUNICATION WITH FIREBASE ===========
import pyrebase

#======== PDF CERTIFICATE GENERATION ===========
from fpdf import FPDF

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'amvi@rto.in': '123456'
}
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#---------------------------------- FUNCTIONS DEFINATIONS ----------------------------------------------------
##################################################################################################################
#GET VEHICLE DATA FROM FIREBASE DATABASE
def get_veh_data(veh_no):
    config = {
    "apiKey": "AIzaSyBNQvthrzSTUkBlpRS6S8zsmH1zLCCxYxM",
    "authDomain": "gov-techathon-16d21.firebaseapp.com",
    "databaseURL": "https://gov-techathon-16d21.firebaseio.com",
    "storageBucket": "gov-techathon-16d21.appspot.com"
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    data  = db.child(veh_no).get()
    if data.val() is not None:
        return pd.Series(data.val(), index = data.val().keys()), True
    else:
        False, False

##################################################################################################################
#PRINT VEHICLE DATA LAYOUT WEB APP
def veh_data_layout(data):
    layout = []
    for idx in data.index:
        rows = dbc.Row(
            dbc.Col(
                dbc.Alert(html.H3(str(idx) + ' : ' + str(data.loc[idx])), color="primary"),
                width={"size": 6, "offset": 3},
            )
        )
        layout.append(rows)
    layout = html.Div(layout)
    return layout

##################################################################################################################
#TESTING OBERVATIONS TABLE ACCORDING RULE-62
def rules_layout():
    df = pd.read_csv('default_rule.csv')
    df = df.dropna()    
    layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i, 'presentation': 'dropdown'} for i in df.columns],
    data = df.to_dict('records'),
    editable=True,
    css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],
    dropdown={
        'Fitment': {
            'options': [{'label': i, 'value': i} for i in ['YES', 'NO']]
        },
        'Rating': {
            'options': [{'label': i, 'value': i} for i in ['YES', 'NO']]
        },
        'Condition': {
            'options': [{'label': i, 'value': i} for i in ['YES', 'NO']]
        },
        'Function': {
            'options': [{'label': i, 'value': i} for i in ['YES', 'NO']]
        },
        'Testing': {
            'options': [{'label': i, 'value': i} for i in ['YES', 'NO']]
        }
    }
    )
    layout = html.Div([
        html.H2('Vechicle Fitness Test Parameters'),
        html.Br(),
        html.H3('Visual Test Parameters'),
        layout,
        html.Br(),
        html.H3('PUC Parameters'),
        dbc.Row([
            dbc.Col(dbc.Input(id="puc_co", placeholder="CO gm/km", type="text")),
            dbc.Col(dbc.Input(id="puc_nox", placeholder="NOx gm/km", type="text")),
            dbc.Col(dbc.Input(id="puc_hc", placeholder="HC gm/km", type="text")),
        ]),
    ])
    return layout

##################################################################################################################
#DISPLAYING UPLOADED IMAGE ON BROWSER
def parse_contents(contents, filename, date):
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        html.Img(src=contents, style={
                'width': '300px',
                'height': '250px'}),
    ])

##################################################################################################################
#IMAGES UPLOAD LAYOUT
def upload_layout():
    #For Front
    front_layout = html.Div([
        dcc.Upload(
            id='front_image',
            children=html.Div([
                'Drag and Drop or Vehicle Images ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
        ),
        html.Div(id = 'front_content',
        style={
                'width': '100%',
                'height': '60px'},
        ),
    ])
    return front_layout

##################################################################################################################
#UPLOAD IMAGE TO FIREBASE
def image_to_cloud(veh_no, image):
    config = {
    "apiKey": "AIzaSyBNQvthrzSTUkBlpRS6S8zsmH1zLCCxYxM",
    "authDomain": "gov-techathon-16d21.firebaseapp.com",
    "databaseURL": "https://gov-techathon-16d21.firebaseio.com",
    "storageBucket": "gov-techathon-16d21.appspot.com"
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    db.child(veh_no).child("Image").push(image)

##################################################################################################################
#PREPARE A CERTIFICATE FOR PERTICULAR VEHICAL IN PDF
def make_certificate(veh_no):
    today = datetime.date.today()
    next_year = today + datetime.timedelta(days=356)
    current_date = today.strftime("%d/%m/%Y")
    next_date = next_year.strftime("%d/%m/%Y")
    pdf = FPDF() 
    pdf.add_page() 
    pdf.set_font("Arial", size = 15, style = 'B') 
    pdf.cell(200, 10, txt = "FORM 38",  ln = 1, align = 'C')
    pdf.set_font("Arial", size = 15, style = 'I') 
    pdf.cell(200, 10, txt = "Refer Rule 62(1)", ln = 2, align = 'C') 
    pdf.set_font("Arial", size = 15) 
    pdf.cell(200, 10, txt = 'CERTIFICATE OF FITNESS', ln = 2, align = 'C')
    pdf.cell(200, 10, txt = '(Applicable in Case of Transport Vehicles only)', ln = 2, align = 'C')
    pdf.cell(200, 10, txt = 'Vehicle No. ' + veh_no + ' is certified as complying with the provisions of the ', ln = 2)
    pdf.cell(200, 10, txt = 'Motor Vehicle Act 1988 and the rules made there under.', ln = 2)
    pdf.cell(200, 10, txt = 'The Certificate expires on ' + next_date, ln = 2)
    pdf.ln()
    pdf.cell(200, 10, txt = 'Printed on ' + current_date, ln = 2)
    pdf.ln()
    pdf.cell(200, 10, txt = 'Signature and Designation of Inspecting Authority', ln = 2, align = 'R')
    # save the pdf with name .pdf 
    pdf.output(veh_no + '.pdf')

##################################################################################################################
#UPLOAD TEST RESULT TO FIREBASE
def upload_test_result(veh_no, result):
    config = {
      "apiKey": "AIzaSyBNQvthrzSTUkBlpRS6S8zsmH1zLCCxYxM",
      "authDomain": "gov-techathon-16d21.firebaseapp.com",
      "databaseURL": "https://gov-techathon-16d21.firebaseio.com",
      "storageBucket": "gov-techathon-16d21.appspot.com"
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    if result:
        #Certificate Status
        db.child(veh_no).child('Vehicle Fitness Certificate').set('Yes')
    else:
        db.child(veh_no).child('Vehicle Fitness Certificate').set('No')
    #Test Date
    today = datetime.date.today()
    current_date = today.strftime("%d/%m/%Y")
    db.child(veh_no).child('Vehicle Fitness Certificatedate').set(current_date)

##################################################################################################################
#DISPLAY TEST RESULT IN BROWSER
def result_layout(test_data, co_val, nox_val, hc_val):
    #Rules data
    test_data = pd.DataFrame.from_dict(test_data)
    test_data = test_data.drop(columns = ['Iteam'])
    test_data = test_data.replace('Yes', 1)
    test_data = test_data.replace('No', 0)
    test_data = test_data.replace('YES', 1)
    test_data = test_data.replace('NO', 0)
    test_data = np.array(test_data)
    actual_data = pd.read_csv('actual_rule.csv')
    actual_data = actual_data.drop(columns = ['Iteam'])
    actual_data = np.array(actual_data)
    rules_result = round((test_data.sum()/actual_data.sum())*100,0)
    rules_status = 'Failed'
    if rules_result > 5:
        rules_status = 'Passed'
    #PUC Result
    if co_val is not None:
        co_val = float(co_val)
    else:
        co_val = 0
    if nox_val is not None:
        nox_val = float(nox_val)
    else:
        nox_val = 0
    if hc_val is not None:  
        hc_val = float(hc_val)
    else:
        hc_val = 0
    co = False
    nox = False
    hc = False
    puc_result = 'Failed'
    if co_val > 1 and co_val < 2.27:
        co = True
    if hc_val > 0.1 and hc_val < 0.16:
        hc = True
    if nox_val > 0.06 and nox_val < 0.082:
        nox = True
    if co and nox and hc:
        puc_result = 'Passed'
    layout = html.Div([
        dbc.Alert('Rules Result : ' + str(rules_result) + ' %', color = 'warning'),
        dbc.Alert('Rules Status : ' + rules_status, color = 'warning'),
        dbc.Alert('PUC Result   : ' + puc_result, color = 'warning'),
    ])
    return layout, rules_status, puc_result

##################################################################################################################
#DASH LAYOUT OF APP
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])
app.config.suppress_callback_exceptions = True
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
app.layout = html.Div([
    html.Div(
    [   
        html.H3('Enter Vehicle Number:'),
        dbc.Input(id="veh_number", placeholder="Enter Vehicle Number", type="text"),
        dbc.Button('Submit', id = 'number_button'),
        html.H4('Vehicle Number Format : SS12MM1234'),
        html.Br(),

    ]),
    html.Div(id = 'veh_data'),
    html.Div(id = 'rules_data'),
    upload_layout(),
    dbc.Row([dbc.Col(dbc.Button('Submit Test Data', id = 'submit_button'), width=4, align="end")], 
    style={'margin-top': '300px'}),
    html.Div(id = 'total_data'),
    Download(id="download"),
])

##################################################################################
#CALLBACK FOR GETTING VEHICLE DATA
@app.callback([Output("veh_data", "children"),
    Output('rules_data', 'children')],
    [Input("veh_number", "value"),
    Input('number_button', 'n_clicks')])
def output_text(number, n_clicks):
    ctx = dash.callback_context
    changed_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if changed_id == 'number_button':
        try:
            data, valid_number = get_veh_data(number)
            if valid_number:
                return veh_data_layout(data), rules_layout()
            else:
                return html.H4('Please, Enter a valid Vehicle Number'), html.H4('')
        except TypeError:
            return html.H4('Please, Enter a valid Vehicle Number Error'), html.H4('')

    else:
        return html.H4(''),html.H4('')

##################################################################################
#CALLBACK FOR UPLOADING VEHICLE IMAGE
@app.callback(Output('front_content', 'children'),
              [Input("veh_number", "value"),
              Input('front_image', 'contents')],
              [State('front_image', 'filename'),
               State('front_image', 'last_modified')])
def update_output(veh_no, list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        image_to_cloud(veh_no, list_of_contents)
        return parse_contents(list_of_contents, list_of_names, list_of_dates)

##################################################################################
#FOR UPLOADING VEHICLE IMAGE AND DATA TO SERVER AND DOWNLOAD CERTIFICATE
@app.callback([Output("total_data", "children"),
    Output("download", "data")],
    [Input("submit_button", "n_clicks"),
    Input('table', 'data'),
    Input('puc_co', 'value'),
    Input('puc_nox', 'value'),
    Input('puc_hc', 'value'),
    Input("veh_number", "value")]
    )
def test_result(n_clicks, test_data, co, nox, hc, val_number):
    ctx = dash.callback_context
    changed_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if changed_id =='submit_button':
        layout, rules_st, puc_st = result_layout(test_data, co, nox, hc)
        if rules_st == 'Passed' and puc_st == 'Passed':
            make_certificate(val_number)
            upload_test_result(val_number, True)
            return layout, send_file(val_number + '.pdf')
        else:
            upload_test_result(val_number, False)
            return layout, send_file('failed_certi.pdf')


if __name__ == '__main__':
    app.run_server()
