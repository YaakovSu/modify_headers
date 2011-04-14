# -*- coding: utf-8 -*- 
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

import urllib2
import logging
import datetime

# import simplejson as json
if request.env.web2py_runtime_gae:
    from django.utils import simplejson as json
else:
    import simplejson as json

def index():

    headers=session.headers
    
    if headers==None or len(headers)<1:
        # try to read headers from the cookies
        
        headers=_load_cookies(request)        
        if headers==None:        
            headers={}
            
        session.headers=headers

        
    form = SQLFORM.factory(
         Field('url', requires=IS_NOT_EMPTY()),
         Field('header'),
         Field('value'),
         Field('result', 'text'),
         Field('time')
         )
         
        
    if form.accepts(request.vars, formname='form_one'):
        response.flash = T('Here you go!!')
        try:
            logging.debug('calling the url %s ' %request.vars.url)
            
            _result=_call_url(form, headers)
                            
            form.vars.result=_result[0]
            form.vars.time=_result[1]
            
            _save_cookies(response, headers)
         
        except Exception, err:
            logging.error('Error: %s\n' %str(err))
                            
            form.vars.result=T('Error %s calling the url.' %str(err))
            response.flash = T('Error!!')
            return dict(form=form, headers=_html_headers(headers))

        
        if request.vars.flag_redirect =='y':
            return form.vars.result
                                
    return dict(form=form, headers=_html_headers(headers))


def _set_headres(headers, req):
    
    if headers:
        for h in headers:
            req.add_header(h, headers[h])
    
    return req
            

        
def _call_url(form, headers):
    
    
    if not form.vars.url.startswith('http'):
        url='http://%s' %form.vars.url
    else:
        url=form.vars.url
        
    # set the url into the session.
    
    session.url=url
    
    req = urllib2.Request(url)
    req= _set_headres(headers, req)
            
    opener = urllib2.build_opener()
    
    start=datetime.datetime.now()    
    res=opener.open(req)    
    end=datetime.datetime.now()
    
    return res.read(), end-start
    
def _html_headers(headers):
    
    list_header=[]
    for h in headers:
        list_header.append(LI('%s:%s  ' %(h, headers[h]), A(DIV('delete', _id='%s' %h, _class='link_delete' ), _href='#')))
                        
    return UL(list_header, _id='list_headers')
    
def add_header():

    headers=session.headers
               
    if (request.vars.header and len(request.vars.header)>0):
        headers[request.vars.header]= request.vars.value
        _save_cookies(response, headers)

          
    return _html_headers(headers).xml()
    
def delete_header():
    
    headers=session.headers
   
    if request.vars.header:
        headers.pop(request.vars.header)
        _save_cookies(response, headers)
    
    return _html_headers(headers).xml()
    
def _save_cookies(response, headers):

    response.cookies['headers'] = json.dumps(headers)
    
    # one month cookies
    response.cookies['headers']['expires'] = 30 * 24 * 60 * 60
    response.cookies['headers']['path'] = '/'
    #response.cookies['headers']['domain'] = response._view_environment['request'].env['remote_addr']
    
def _load_cookies(request):
           
    if request.cookies.has_key('headers'):    
            
        myc=request.cookies['headers']    
                                  
        return json.loads(myc.value)
       
           
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
