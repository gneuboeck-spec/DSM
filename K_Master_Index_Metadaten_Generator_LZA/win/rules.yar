rule DOC {
    meta: pronom_id = "fmt/40" note = "Microsoft Word 97-2003"
    strings:
        $magic = {D0 CF 11 E0 A1 B1 1A E1}
        $word1 = "WordDocument"
        $word2 = "Microsoft Word"
    condition:
        $magic at 0 and 1 of ($word1, $word2)
}

rule DOCX {
    meta: pronom_id = "fmt/412" note = "Microsoft Word Open XML (DOCX)"
    strings:
        $zip = {50 4B 03 04}
        $docx = "word/document.xml"
    condition:
        $zip at 0 and $docx
}

rule RTF {
    meta: pronom_id = "fmt/199" note = "Rich Text Format"
    strings: $rtf = "{\\rtf"
    condition: $rtf at 0
}

rule PAGES {
    meta: note = "Apple Pages"
    strings:
        $zip = {50 4B 03 04}
        $xml = "index.xml"
    condition: $zip at 0 and $xml
}

rule SAM {
    meta: note = "Lotus AmiPro SAM format"
    strings:
        $a1 = "[ver]"
        $a2 = "[sty]"
        $a3 = "[files]"
        $a4 = "[charset]"
        $a5 = "[revisions]"
    condition: all of ($a1, $a2, $a3, $a4, $a5) in (0..512)
}

rule DBX {
    meta:
        pronom_id = "fmt/838"
        note = "Outlook Express Mailbox (DBX)"
    strings:
        $dbx_magic = {CF AD 12 FE}
        $dbx_str = "Folders.dbx"
    condition:
        $dbx_magic at 0 or $dbx_str
}

rule EML {
    meta:
        note = "Email Message (EML)"
        pronom_id = "x-fmt/101"
    strings:
        $from = "From:" nocase
        $to = "To:" nocase
        $subject = "Subject:" nocase
        $date = "Date:" nocase
        $mime_version = "MIME-Version:" nocase
    condition:
        ($from at 0 or $subject at 0 or $date at 0) or
        (2 of ($from, $to, $subject, $date, $mime_version))
}

rule JSON {
    meta: pronom_id = "fmt/289" note = "JSON"
    strings: $json = "{"
    condition: $json at 0
}

rule PS {
    meta:
        pronom_id = "fmt/134"
        note = "Adobe PostScript (.ps)"
    strings:
        $header = "%!PS-Adobe-"
    condition:
        $header at 0
}

rule PDF {
    meta:
        pronom_id = "fmt/18"
        note = "Adobe PDF (kein PDF/A)"
    strings:
        $pdf = {25 50 44 46 2D}
        $pdfaid = "xmlns:pdfaid=\"http://www.aiim.org/pdfa/ns/id/\""
    condition:
        $pdf at 0 and not $pdfaid
}

rule PDFA {
    meta:
        pronom_id = "fmt/476"
        note = "PDF/A - ISO 19005 (Archivformat)"
    strings:
        $pdf = {25 50 44 46 2D}
        $xmp1 = "<pdfaid:part>1</pdfaid:part>"
        $xmp2 = "<pdfaid:part>2</pdfaid:part>"
        $xmp3 = "<pdfaid:part>3</pdfaid:part>"
        $namespace = "xmlns:pdfaid=\"http://www.aiim.org/pdfa/ns/id/\""
    condition:
        $pdf at 0 and $namespace and 1 of ($xmp1, $xmp2, $xmp3)
}

// Praesentationen

rule PPT {
    meta: pronom_id = "fmt/126" note = "Microsoft PowerPoint 97-2003"
    strings:
        $magic = {D0 CF 11 E0 A1 B1 1A E1}
        $ppt = "PowerPoint Document"
    condition:
        $magic at 0 and $ppt
}

rule PPTX {
    meta: pronom_id = "fmt/215" note = "Microsoft PowerPoint Open XML (PPTX)"
    strings:
        $zip = {50 4B 03 04}
        $pptx = "ppt/presentation.xml"
    condition: $zip at 0 and $pptx
}

rule ODP {
    meta: pronom_id = "fmt/291" note = "OpenDocument Presentation (ODP)"
    strings:
        $zip = {50 4B 03 04}
        $content = "content.xml"
        $mimetype = "application/vnd.oasis.opendocument.presentation"
    condition: $zip at 0 and any of ($content, $mimetype)
}

rule KEY {
    meta: note = "Apple Keynote"
    strings:
        $zip = {50 4B 03 04}
        $index = "index.apxl"
    condition: $zip at 0 and $index
}

rule PRZ {
    meta: note = "Lotus Freelance Graphics (PRZ)"
    strings:
        $magic = {A0 46 1D F0}
    condition: $magic at 0
}

rule SHW {
    meta: note = "Corel Presentations (SHW / Harvard Graphics)"
    strings:
        $magic1 = {00 00 1E 00 03 00 00 00}
        $magic2 = {48 47 46 38}
    condition: 1 of ($magic1, $magic2)
}

// Tabellen

rule XLS {
    meta: pronom_id = "fmt/58" note = "Microsoft Excel 97-2003"
    strings:
        $magic = {D0 CF 11 E0 A1 B1 1A E1}
        $xls = "Workbook"
    condition: $magic at 0 and $xls
}

rule CSV {
    meta: note = "Comma-Separated Values (heuristisch)"
    strings:
        // Sucht nach einer Zeile mit mindestens einem Komma zwischen Zeichen, die keine Zeilenumbrüche sind.
        $csv_line = /(\r\n|\n|\r|^)[^\r\n,]+(,[^\r\n,]+)+/
    condition:
        // Die Regel ist erfuellt, wenn das Muster mindestens 3 Mal in den ersten 2048 Bytes gefunden wird.
        // Dies ist ein viel stärkerer Indikator für eine CSV-Datei als nur ein einziger Treffer.
        // Das erhöht die Zuverlässigkeit und verhindert das Scannen der gesamten Datei.
        3 of ($csv_line) in (0..2048) and

        // Ausschluss bekannter Text- oder Binärformate, die Kommas enthalten koennten.
        not (
            uint32be(0) == 0x3C3F786D or // "<?xm" (XML)
            uint32be(0) == 0x7B5C7274 or // "{\rtf" (RTF)
            uint32be(0) == 0x25504446 or // "%PDF" (PDF)
            (uint32be(0) | 0x20202020) == 0x3c21646f or // "<!do" (HTML/XML Doctype, case-insensitive)
            (uint32be(0) | 0x20202020) == 0x3c68746d // "html" (HTML-Tag, case-insensitive)
        )
}

// Audio

rule MP3 {
    meta: pronom_id = "fmt/134" note = "MP3 Audio"
    strings:
        $frame_sync = {FF FB}
        $frame_sync_alt = {FF F3}
        $frame_sync_alt2 = {FF F2}
        $id3v2 = "ID3"
    condition:
        $frame_sync at 0 or
        $frame_sync_alt at 0 or
        $frame_sync_alt2 at 0 or
        $id3v2 at 0
}

rule WAV {
    meta: pronom_id = "fmt/141" note = "WAVE Audio"
    strings:
        $riff = "RIFF"
        $wave = "WAVE"
    condition: $riff at 0 and $wave in (8..20)
}

rule FLAC {
    meta: pronom_id = "fmt/375" note = "FLAC"
    strings: $flac = "fLaC"
    condition: $flac at 0
}

// Video

rule MP4 {
    meta: note = "MPEG-4 Video"
    strings: $ftyp = "ftyp"
    condition: $ftyp in (0..4096)
}

rule AVI {
    meta: pronom_id = "fmt/6" note = "AVI Video"
    strings:
        $riff = "RIFF"
        $avi = "AVI "
    condition: $riff at 0 and $avi in (8..20)
}

rule MKV {
    meta: note = "Matroska Video"
    strings: $mkv = {1A 45 DF A3}
    condition: $mkv at 0
}

// Bilder

rule JPEG {
    meta: pronom_id = "fmt/43" note = "JPEG"
    strings: $jpg = {FF D8 FF}
    condition: $jpg at 0
}

rule PNG {
    meta: pronom_id = "fmt/11" note = "PNG"
    strings: $png = {89 50 4E 47 0D 0A 1A 0A}
    condition: $png at 0
}

rule TIFF {
    meta: pronom_id = "fmt/353" note = "TIFF"
    strings:
        $tiff1 = {49 49 2A 00}
        $tiff2 = {4D 4D 00 2A}
    condition: $tiff1 at 0 or $tiff2 at 0
}

rule GIF {
    meta: pronom_id = "fmt/4" note = "GIF"
    strings:
        $gif1 = "GIF87a"
        $gif2 = "GIF89a"
    condition: $gif1 at 0 or $gif2 at 0
}

rule BMP {
    meta: pronom_id = "x-fmt/117" note = "Windows Bitmap (BMP)"
    strings: $bmp = {42 4D}
    condition: $bmp at 0
}

// XML

rule XML {
    meta: pronom_id = "fmt/151" note = "Generic XML (nicht MusicXML)"
    strings:
        $start = "<?xml"
        $score1 = "<score-partwise"
        $score2 = "<score-timewise"
    condition:
        $start at 0 and not 1 of ($score1, $score2)
}

rule MUSICXML {
    meta: note = "MusicXML uncompressed"
    strings:
        $xml = "<?xml"
        $score1 = "<score-partwise"
        $score2 = "<score-timewise"
    condition: $xml at 0 and 1 of ($score1, $score2)
}

rule MXL {
    meta: note = "MusicXML compressed (.mxl)"
    strings:
        $zip = {50 4B 03 04}
        $content = "META-INF/container.xml"
    condition: $zip at 0 and $content
}

// HTML / TXT

rule HTML {
    meta: pronom_id = "x-fmt/111" note = "HyperText Markup Language (HTML)"
    strings:
        $doctype_html = "<!DOCTYPE html" nocase
        $html_tag = "<html" nocase
        $body_tag = "<body" nocase
        $head_tag = "<head" nocase
    condition:
        ($doctype_html at 0 or $html_tag at 0) and ($body_tag or $head_tag)
}

rule XHTML {
    meta: pronom_id = "fmt/101" note = "Extensible HyperText Markup Language (XHTML)"
    strings:
        $doctype_xhtml = "<!DOCTYPE html PUBLIC" nocase
        $html_xmlns = "xmlns=\"http://www.w3.org/1999/xhtml\"" nocase
        $html_tag = "<html" nocase
        $body_tag = "<body" nocase
        $head_tag = "<head" nocase
    condition:
        $doctype_xhtml at 0 and $html_xmlns and ($html_tag and ($body_tag or $head_tag))
}

// HINWEIS: TXT ist eine Fallback-Regel und wird erst nach den spezifischeren Regeln ausgewertet.
// Sie kann fehlerhaft sein, wenn eine Datei keiner anderen Regel entspricht.
rule TXT {
    meta: pronom_id = "x-fmt/111" note = "Plain Text File"
    condition:
        // Trifft zu, WENN eine Datei KEINE der bekannten Binär-Signaturen am Anfang hat.
        // Diese Negativ-Prüfung erzeugt keine "too many matches" Fehler.
        filesize > 0 and
        not (
            uint32be(0) == 0x504B0304 or // ZIP
            uint32be(0) == 0x25504446 or // PDF
            uint32be(0) == 0xD0CF11E0 or // OLE (DOC, XLS)
            uint32be(0) == 0x89504E47 or // PNG
            uint16be(0) == 0xFFD8    or // JPEG
            uint16be(0) == 0x424D    or // BMP
            uint16be(0) == 0x4949    or // TIFF (Little Endian)
            uint16be(0) == 0x4D4D    or // TIFF (Big Endian)
            uint32be(0) == 0x47494638    // GIF ("GIF8")
        )
}

// Archive

rule ZIP_ARCHIVE {
    meta: pronom_id = "fmt/111" note = "Generic ZIP Archive"
    strings:
        $zip_magic = {50 4B 03 04}
        $zip_central_dir = {50 4B 01 02}
        $zip_end_of_central_dir = {50 4B 05 06}
    condition:
        $zip_magic at 0 or
        ($zip_central_dir and $zip_end_of_central_dir)
}