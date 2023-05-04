# Appendix 3: Example Config

The following is the example config that has been built throughout this
documentation. The raw file can be accessed [here](example.isi).

    create host
    yoda
    luke
    leia
    obi-wan
    han
    chewy
    beru
    end
    
    create tag
    newark
    princeton
    cherryhill
    physical
    virtual
    server
    workstation
    laptop
    end
    
    tag newark set group location
    tag princeton set group location
    tag cherryhill set group location
    tag physical set group physicality
    tag virtual set group physicality
    tag server set group type
    tag workstation set group type
    tag laptop set group type
    
    host yoda tag add
    newark
    physical
    server
    end
    
    host luke tag add
    newark
    virtual
    server
    end
    
    host leia tag add
    princeton
    physical
    workstation
    end
    
    host obi-wan tag add
    princeton
    physical
    workstation
    end
    
    host han tag add
    cherryhill
    physical
    laptop
    end
    
    host chewy tag add
    cherryhill
    physical
    server
    end
    
    host beru tag add
    cherryhill
    virtual
    server
    end
     

