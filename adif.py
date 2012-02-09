#!/usr/bin/python

from datetime         import datetime
from rsclib.autosuper import autosuper

class ADIF_Syntax_Error (RuntimeError)  : pass
class ADIF_EOF          (StandardError) : pass

class ADIF_Parse (autosuper) :
    def __init__ (self, fd, lineno = 1) :
        self.__super.__init__ ()
        self.fd     = fd
        self.lineno = lineno
        self.dict   = {}
    # end def __init__

    def get_tags (self, endtag) :
        for k, v in self.get_tag () :
            if k == endtag :
                if v :
                    raise ADIF_Syntax_Error, "%s: Invalid %s" \
                        % (self.lineno, endtag)
                return
            else :
                self.dict [k] = v
    # end def get_tags

    def get_tag (self) :
        count  = 0
        tag    = []
        value  = []
        state  = 'start'

        c = self.fd.read (1)
        while (c) :
            if state == 'start' :
                if c.isspace () :
                    if c == '\n' :
                        self.lineno += 1
                elif c == '<' :
                    state = 'tag'
                else :
                    raise ADIF_Syntax_Error, \
                        '%s: Expected tag start' % self.lineno
            elif state == 'tag' :
                if c == '>' or c == ':' :
                    if len (tag) == 0 :
                        raise ADIF_Syntax_Error, '%s: Empty tag' % self.lineno
                    tag   = ''.join (tag)
                    state = 'length'
                    if c == '>' :
                        yield ''.join (tag), ''
                        tag   = []
                        value = []
                        state = 'start'
                else :
                    tag.append (c)
            elif state == 'length' :
                if c == '>' :
                    try :
                        count = int (''.join (value))
                    except ValueError :
                        raise ADIF_Syntax_Error, '%s: Invalid count: %s' \
                            % (self.lineno, ''.join (value))
                    value = []
                    state = 'value'
                else :
                    value.append (c)
            elif state == 'value' :
                value.append (c)
                count -= 1
                if count == 0 :
                    value = ''.join (value)
                    yield (tag, value)
                    tag   = []
                    value = []
                    state = 'start'
            else :
                assert (0)
            c = self.fd.read (1)
    # end def get_tag

    def __getitem__ (self, name) :
        return self.dict [name]
    # end def __getitem__

    def __contains__ (self, name) :
        return name in self.dict
    # end def __contains__
    has_key = __contains__
# end class ADIF_Parse

class ADIF_Record (ADIF_Parse) :
    """ Represents a QSO record in ADIF format
        Common fields: BAND, CALL, FREQ, MODE, QSO_DATE, RST_RCVD,
        RST_SENT, TIME_OFF, TIME_ON, GRIDSQUARE
    """

    cabrillo_fields  = \
        [ 'FRQINT:5'
        , 'MODE:2'
        , 'ISODATE:10'
        , 'TIME_OFF:4'
        , 'OWN_CALL:13'
        , 'RST_SENT:3'
        , 'CALL:13'
        , 'RST_RCVD:3'
        , 'GRIDSQUARE:4'
        ]

    def __init__ (self, adif, fd, lineno) :
        """ consume one record from fd """
        self.__super.__init__ (fd, lineno)
        self.adif = adif
        self.fd   = fd
        self.get_tags ('EOR')
        if not self.dict :
            raise ADIF_EOF
    # end def __init__

    def as_cabrillo (self, fields = None) :
        x = fields or self.cabrillo_fields
        fields = []
        for f in x :
            a, b = f.split (':')
            fields.append ((a, int (b)))
        r = ['QSO:']
        for f, l in fields :
            fmt = '%-' + str (l) + '.' + str (l) + 's'
            r.append (fmt % self [f])
        return ' '.join (r)
    # end def as_cabrillo

    def __getitem__ (self, name) :
        if name == 'FRQINT' :
            return str (int (float (self.dict ['FREQ']) * 1000 + 0.5))
        elif name == 'MODE' and self.adif.modemap :
            return self.adif.modemap.get \
                ( self.dict ['MODE']
                , self.adif.modemap.get ('default', self.dict ['MODE'])
                )
        elif name == 'ISODATE' :
            dt = datetime.strptime (self.dict ['QSO_DATE'], '%Y%m%d')
            return dt.strftime ('%Y-%m-%d')
        try :
            return self.__super.__getitem__ (name)
        except KeyError :
            return self.adif [name]
    # end def __getitem__

    def __contains__ (self, name) :
        if name in ('FRQINT', 'ISODATE') :
            return True
        if name == 'MODE' and self.adif.modemap :
            return True
        return self.__super.has_key (name) or self.adif.has_key (name)
    # end def __contains__
    has_key = __contains__
# end class ADIF_Record

class ADIF (ADIF_Parse) :

    modemap = {}

    def __init__ (self, fd, lineno = 1, callsign = None, ** kw) :
        self.__super.__init__ (fd, lineno)
        self.callsign = callsign
        self.dict.update (kw)
        if callsign :
            self.dict ['OWN_CALL'] = callsign
        self.records  = []
        l = fd.readline ()
        f, fn = l.split (': ')
        if f != 'File' :
            raise ADIF_Syntax_Error, "File header not found", self.lineno
        self.filename = fn.rstrip ('\r\n')
        self.lineno += 1
        self.get_tags ('EOH')
        while (1) :
            try :
                self.records.append (ADIF_Record (self, fd, self.lineno))
            except ADIF_EOF :
                break
    # end def __init__

    def as_cabrillo (self, fields = None, cabrillo = (), **kw) :
        s = []
        for k, v in cabrillo :
            s.append ('%s: %s' % (k.upper (), v))
        for k, v in kw.iteritems () :
            s.append ('%s: %s' % (k.upper (), v))
        for r in self.records :
            s.append (r.as_cabrillo (fields))
        s.append ('END_OF_LOG:')
        return '\n'.join (s)
    # end def as_cabrillo

    def set_modemap (self, modemap) :
        """ Set a map for mapping modes in self ['MODE'] to something
            else. May specify 'default' as a key for a default mapping
            if nothing is found.
        """
        self.modemap = modemap
    # end def set_modemap

# end class ADIF

if __name__ == '__main__' :
    import sys
    adif = ADIF (sys.stdin)
    d = {'START-OF-LOG' : '2.0'}
    print adif.as_cabrillo (callsign = 'OE3RSU', cabrillo = d)
