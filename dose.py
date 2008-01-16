from dose_f import *

if __name__ == "__main__":
    params_site.__dict__['u_h'] = 11
    params_site.derive_windspeed_d_zo()
    print "u_h:", params_site.u_h, params_site.__dict__['u_h'], getattr(params_site, 'u_h')
    print "u_d:", params_site.u_d, params_site.__dict__['u_d'], getattr(params_site, 'u_d')
    setattr(params_site, 'u_h', 12)
    params_site.derive_windspeed_d_zo()
    print "u_h:", params_site.u_h, params_site.__dict__['u_h'], getattr(params_site, 'u_h')
    print "u_d:", params_site.u_d, params_site.__dict__['u_d'], getattr(params_site, 'u_d')
