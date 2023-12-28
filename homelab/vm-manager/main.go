package main

import (
	"encoding/xml"
	"fmt"
	"gosrc"
)

// const xmldump = `
// <metadata>
// 	<libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0">
// 		<libosinfo:os id="http://debian.org/debian/11"/>
// 	</libosinfo:libosinfo>
// </metadata>
// `

// type Os struct {
// 	XMLName xml.Name `xml:"libosinfo:os"`
// 	Id string `xml:"id,attr"`
// }

// type Libosinfo struct {
// 	XMLName xml.Name `xml:"libosinfo:libosinfo"`
// 	Libosinfo string `xml:"xmlns:libosinfo,attr"`
// 	Os Os `xml:"libosinfo:os"`
// }

// type Metadata struct {
//  	XMLName xml.Name `xml:"metadata"`
//  	Libosinfo Libosinfo `xml:"libosinfo:libosinfo"`
// }


func main() {
	// buf := bytes.NewBufferString("")
	// encoder := xml.NewEncoder(buf)

	// metadata := Metadata{
	// 	XMLName:   xml.Name{},
	// 	Libosinfo: Libosinfo{
	// 		Libosinfo: "http://libosinfo.org/xmlns/libvirt/domain/1.0",
	// 		Os:        Os{
	// 			Id: "http://debian.org/debian/11",
	// 		},
	// 	},
	// }

	domain := gosrc.GetDefaultDomain("machine name", 123123, 4, "://placeholder/libos/meta", "/fake/sourceImage/path", "/fake/cidata/path", "/root/workspace")

	marshalled, err := xml.MarshalIndent(domain, "", "  ")
	if err != nil {
		panic(err)
	}

	fmt.Println(string(marshalled))
}
