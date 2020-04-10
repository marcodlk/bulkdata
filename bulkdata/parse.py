from .error import EmptyLineError


class BDFParser:
    
    BEGINBULK = "BEGIN BULK"
    ENDDATA = "ENDDATA"
    MAXLINELENGTH = 80
    FIELDWIDTH = 8
    FIELDSPERLINE = 10
    FIELDSPERBODY = 8
    
    def __init__(self, bdf_str):
        # bdf_str = self.expand_tabs(bdf_str)
        self.bds = self.ignore_enddata(bdf_str)
        self.lines = self.bds.split("\n")
        self.remove_comments()
        self.line_idx = 0
        self.cards = []
        
    def current_line(self):
        return self.lines[self.line_idx]
    
    def increment_line(self, i=1):
        self.line_idx += i
        return self.current_line()
    
    def ignore_enddata(self, bdf_str):
        
        try:
            enddata_i = bdf_str.index(self.ENDDATA)
        except ValueError:
            return bdf_str
        else:
            return bdf_str[:enddata_i]
            
    def is_comment(self, line):
        line = line.lstrip()
        return not line or line[0] == "$"
        
    def remove_comments(self):
        comments_i = [
            i 
            for i in range(len(self.lines))
            if self.is_comment(self.lines[i])
        ]
        for i in reversed(comments_i):
            del self.lines[i]

    def parse_header(self):

        beginbulk_i = None
        for line_idx, line in enumerate(self.lines):
            if self.BEGINBULK in line:
                beginbulk_i = line_idx
                break

        if beginbulk_i is None:
            return ""
        else:
            self.line_idx = beginbulk_i + 1
            return "\n".join(self.lines[:beginbulk_i])
    
    def is_line_free(self, line):
        return "," in line
    
    def parse_fields(self, fields):
        fieldsperline = self.FIELDSPERLINE
        fieldsperbody = self.FIELDSPERBODY
        numfields = len(fields)
        head, body, tail = None, [], None
        if numfields == 0:
            raise EmptyLineError()
        if numfields > 0:
            head = fields[0]
        if numfields > 1:
            body = fields[1:]
        if numfields == fieldsperline:
            tail = body.pop(-1)
        # missing fields are blank fields
        nummissing  = fieldsperbody - len(body)
        if nummissing > 0:
            body.extend(["" for _ in range(nummissing)])
        return head, body, tail
    
    def parse_line_free(self, line):
        fields = line.rstrip(",").split(",")
        return self.parse_fields(fields)
    
    def parse_line_fixed(self, line):
        fieldwidth = self.FIELDWIDTH
        length = len(line)
        fields = [line[i:i+fieldwidth]
                  for i in range(0, length, fieldwidth)]
        return self.parse_fields(fields)
    
    def parse_line(self, line):
        
        if self.is_line_free(line):
            return self.parse_line_free(line)

        else:
            return self.parse_line_fixed(line)
        
    def parse_card(self):
        
        line = self.current_line()
        name, fields, tail = self.parse_line(line)
        
        while True:
            
            try:
                next_line = self.increment_line()
            except IndexError:
                break

            next_head, next_fields, next_tail = self.parse_line(next_line)
            
            if not tail:
                next_head = next_head.strip()
                if next_head and not ("+" in next_head):
                    break

            tail = next_tail
            fields.extend(next_fields)

        # pop trailing blank fields
        for i in reversed(range(len(fields))):
            if not fields[i].strip():
                del fields[i]
            else:
                break

        return name, fields
            
    def endofbdf(self):
        return self.line_idx == len(self.lines)
        
    def parse(self):
        
        header = self.parse_header()
        
        cards = []
        
        while not self.endofbdf():
            
            card = self.parse_card()
            cards.append(card)
            
        return header, cards