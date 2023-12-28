package gosrc

import (
	"encoding/xml"
	"fmt"
)

type OS struct {
	ID   string `xml:"id,attr"`
}

type Libosinfo struct {
	Libosinfo string `xml:"xmlns:libosinfo,attr"`
	OS        OS `xml:"libosinfo:os"`
}

type VmManager struct {
	Text     string `xml:",chardata"`
	Internal string `xml:"xmlns:internal,attr"`
}

type Metadata struct {
	Libosinfo Libosinfo `xml:"libosinfo:libosinfo"`
	VmManager VmManager `xml:"internal:vm_manager"`
}

type Memory struct {
	Text string `xml:",chardata"`
	Unit string `xml:"unit,attr"`
}

// type VCPU struct {
// 		Text      string `xml:",chardata"`
// 	}

type Boot struct {
	Dev  string `xml:"dev,attr"`
}

type OS2 struct {
	Type string `xml:"type"`
	Boot Boot `xml:"boot"`
}

type Vmport struct {
	State string `xml:"state,attr"`
}

type Features struct {
	Acpi any `xml:"acpi,omitempty"`
	Apic any `xml:"apic,omitempty"`
	Vmport Vmport `xml:"vmport"`
}

type CPU struct {
	Mode       string `xml:"mode,attr"`
	Check      string `xml:"check,attr"`
	Migratable string `xml:"migratable,attr"`
}

type Timer struct {
	Name       string `xml:"name,attr"`
	Present    *string `xml:"present,attr,omitempty"`
	Tickpolicy *string `xml:"tickpolicy,attr,omitempty"`
}

type Clock struct {
		Offset string `xml:"offset,attr"`
		Timer  []Timer `xml:"timer"`
	}

type Enabler struct {
			Enabled string `xml:"enabled,attr"`
		}

type PowerManagement struct {
		SuspendToMem Enabler `xml:"suspend-to-mem"`
		SuspendToDisk Enabler `xml:"suspend-to-disk"`
	}

type Driver struct {
		Name string `xml:"name,attr"`
		Type string `xml:"type,attr"`
	}

type Source struct {
	File  *string `xml:"file,attr,omitempty"`
	Network *string `xml:"network,attr,omitempty"`
	Bridge  *string `xml:"bridge,attr,omitempty"`
	Path   *string `xml:"path,attr,omitempty"`
	Append   *string `xml:"append,attr,omitempty"`
}

type Target struct {
	Dev  *string `xml:"dev,attr,omitempty"`
	Bus  *string `xml:"bus,attr,omitempty"`
	Port *string `xml:"port,attr,omitempty"`
	Type  *string `xml:"type,attr,omitempty"`
	Name  *string `xml:"name,attr,omitempty"`
	// State *string `xml:"state,attr,omitempty"`
	}


type Disk struct {
	Type   string `xml:"type,attr"`
	Device string `xml:"device,attr"`
	Driver Driver `xml:"driver"`
	Source Source `xml:"source"`
	Target Target `xml:"target"`
	Readonly any `xml:"readonly,omitempty"`
}

type Interface struct {
	Type string `xml:"type,attr"`
	Source Source `xml:"source"`
}

type Serial struct {
	Type   string `xml:"type,attr"`
	Source Source `xml:"source"`
}

type Console struct {
	Type   string `xml:"type,attr"`
	Source Source `xml:"source"`
	Target Target `xml:"target"`
}

type Channel struct {
	Type   string `xml:"type,attr"`
	Target Target `xml:"target"`
}

type Listen struct {
		Type    string `xml:"type,attr"`
		Address string `xml:"address,attr"`
	}

type Image struct {
		Compression string `xml:"compression,attr"`
	}

type Graphics struct {
	Type       string `xml:"type,attr"`
	Port       string `xml:"port,attr"`
	Autoport   string `xml:"autoport,attr"`
	AttrListen string `xml:"listen,attr"`
	Listen  Listen `xml:"listen"`
	Image Image `xml:"image"`
}

type Sound struct {
			Model string `xml:"model,attr"`
		}

type Audio struct {
			ID   string `xml:"id,attr"`
			Type string `xml:"type,attr"`
		}


type Model struct {
		Type    string `xml:"type,attr"`
		Heads   string `xml:"heads,attr"`
		Primary string `xml:"primary,attr"`
	}

type Video struct {
	Model Model `xml:"model"`
}

type MemballoonModel struct {
	Model string `xml:"model,attr"`
}

type Backend struct {
	Text  string `xml:",chardata"`
	Model string `xml:"model,attr"`
}

type RNG struct {
	Model   string `xml:"model,attr"`
	Backend Backend `xml:"backend"`
}

type Devices struct {
		Emulator string `xml:"emulator"`
		Disks []Disk `xml:"disk"`
		Interface Interface `xml:"interface"`
		Serial Serial `xml:"serial"`
		Console Console `xml:"console"`
		Channel Channel `xml:"channel"`
		Graphics Graphics `xml:"graphics"`
		Sound Sound `xml:"sound"`
		Audio Audio `xml:"audio"`
		Video Video `xml:"video"`
		Memballoon MemballoonModel `xml:"memballoon"`
		Rng RNG `xml:"rng"`
	}

type SecLabel struct {
	Type    string `xml:"type,attr"`
	Model   string `xml:"model,attr"`
	Relabel string `xml:"relabel,attr"`
	Label   string `xml:"label"`
}

type Domain struct {
	XMLName xml.Name `xml:"domain"`
	Type    string   `xml:"type,attr"`
	Name    string `xml:"name"`
	Metadata Metadata `xml:"metadata"`
	Memory Memory `xml:"memory"`
	VCPU string `xml:"vcpu"`
	ResourcePartition string `xml:"resource>partition"`
	OS OS2 `xml:"os"`
	Features Features `xml:"features"`
	CPU CPU `xml:"cpu"`
	Clock Clock `xml:"clock"`
	OnPoweroff string `xml:"on_poweroff"`
	OnReboot string `xml:"on_reboot"`
	OnCrash string `xml:"on_crash"`
	PowerManagement PowerManagement `xml:"pm"`
	Devices Devices `xml:"devices"`
	Seclabel SecLabel `xml:"seclabel"`
}

func GetDefaultDomain(name string, memory uint64, vcpus uint8, libosMeta string, sourceImageFile string, cidataFilePath string, workspacePath string) *Domain {
	catchup := "catchup"
	delay := "delay"
	no := "no"
	devVDA := "vda"
	virtio := "virtio"
	devSDA := "sda"
	busSATA := "sata"
	networkDefault := "default"
	networkBridge := "virbr0"
	channelName := "org.qemu.guest_agent.0"
	serialSourcePath := fmt.Sprintf("%s/serial.log", workspacePath)
	on := "on"

	return &Domain{
		Type:              "kvm",
		Name:              name,
		Metadata:          Metadata{
			Libosinfo: Libosinfo{
				Libosinfo: "http://libosinfo.org/xmlns/libvirt/domain/1.0",
				OS:        OS{
					ID:   libosMeta,
				},
			},
			VmManager: VmManager{
				Internal: "https://internal.local",
				Text: "hello from golang!",
			},
		},
		Memory:            Memory{
			Text: fmt.Sprintf("%d", memory),
			Unit: "KiB",
		},
		VCPU:        fmt.Sprintf("%d", vcpus),
		ResourcePartition: "/machine",
		OS:                OS2{
			Type: "hvm",
			Boot: Boot{
				Dev: "hd",
			},
		},
		Features:          Features{
			Acpi:   "",
			Apic:   "",
			Vmport: Vmport{
				State: "off",
			},
		},
		CPU:               CPU{
			Mode:       "host-passthrough",
			Check:      "none",
			Migratable: "on",
		},
		Clock:             Clock{
			Offset: "utc",
			Timer:  []Timer{
				{
					Name:       "rtc",
					Tickpolicy: &catchup,
				},
				{
					Name:       "pit",
					Tickpolicy: &delay,
				},
				{
					Name:       "hpet",
					Present: &no,
				},
			},
		},
		OnPoweroff:        "destroy",
		OnReboot:          "restart",
		OnCrash:           "destroy",
		PowerManagement:   PowerManagement{
			SuspendToMem:  Enabler{
				Enabled: "no",
			},
			SuspendToDisk: Enabler{
				Enabled: "no",
			},
		},
		Devices:           Devices{
			Emulator: "/usr/bin/qemu-system-x86_64",
			Disks:      []Disk{
				{
					Type: "file",
					Device:   "disk",
					Driver:   Driver{
						Name: "qemu",
						Type: "qcow2",
					},
					Source:   Source{
						File:    &sourceImageFile,
					},
					Target:   Target{
						Dev:  &devVDA,
						Bus:  &virtio,
					},
				},
				{
					Type: "file",
					Device: "cdrom",
					Driver:   Driver{
						Name: "qemu",
						Type: "raw",
					},
					Source:   Source{
						File: &cidataFilePath,
					},
					Target:   Target{
						Dev: &devSDA,
						Bus: &busSATA,
					},
					Readonly: "",
				},
			},
			Interface: Interface{
				Type:   "network",
				Source: Source{
					Network: &networkDefault,
					Bridge:  &networkBridge,
				},
			},
			Graphics: Graphics{
				Type:       "spice",
				Port:       "-1",
				Autoport:   "yes",
				AttrListen: "127.0.0.1",
				Listen:     Listen{
					Type:    "address",
					Address: "127.0.0.1",
				},
				Image:      Image{
					Compression: "off",
				},
			},
			Sound: Sound{
				Model: "ich9",
			},
			Audio: Audio{
				ID:   "1",
				Type: "spice",
			},
			Video: Video{
				Model: Model{
					Type:    "virtio",
					Heads:   "1",
					Primary: "yes",
				},
			},
			Memballoon: MemballoonModel{
				Model: "virtio",
			},
			Rng: RNG{
				Model:   "virtio",
				Backend: Backend{
					Model: "random",
					Text:  "/dev/urandom",
				},
			},
			Serial: Serial{
				Type:   "file",
				Source: Source{
					Path:    &serialSourcePath,
					Append: &on,
				},
			},
			Channel: Channel{
				Type:   "unix",
				Target: Target{
					Type: &virtio,
					Name: &channelName,
				},
			},
		},
		Seclabel: SecLabel{
			Type:    "dynamic",
			Model:   "dac",
			Relabel: "yes",
			Label:   "+0:+0",
		},
	}
}
