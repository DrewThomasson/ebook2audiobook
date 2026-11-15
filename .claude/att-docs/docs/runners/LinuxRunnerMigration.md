# Linux runner migration

Standing up an Ubuntu guest on the work laptop and moving every self-hosted job
onto it.

This file lives in this repository rather than the AZDO repository because it names
runners, workflows, share paths, and the hosted provider on nearly every line, and none
of those resolve on the work side.

Keep it current as the build proceeds. A step that turns out to be wrong gets
rewritten to say what actually works, and its status line moves. Do not annotate
what changed; the file describes the build as it stands.

## Status

| Phase | What it covers | Status |
| --- | --- | --- |
| 0 | Blockers: virtualization, host memory, credential sign-off | Cleared 2026-09-01 |
| 1 | Create the guest | Done 2026-09-01 |
| 2 | Network reachability | Passed 2026-09-01 |
| 3 | Corporate certificate chain | Done 2026-09-01 |
| 4 | Node and dependencies | Done 2026-09-01 |
| 5 | Oracle Instant Client | Done 2026-09-01 |
| 6 | Artifact share mount | Done 2026-09-08 |
| 7 | Browsers | Done 2026-09-01 |
| 8 | Register the runner | Done 2026-09-03, three instances |
| 9 | Login spike, the check that decides the migration | Answered 2026-09-03 |

Repository work is tracked separately as issues 1527 (port the four runner
scripts to bash), 1528 (port the seventeen workflow steps), and 1529 (flip the
runner label and walk the suites). Phase 9 has returned its verdict, so all
three are clear to start.

## Where to resume

Phase 9 is answered. A CCA spec run on the guest reaches the application at
`cnuat.ocfs.ny.gov/conxcomp` with the impersonated worker's name in the header,
and the page renders with its styling and its scripts intact. The browser
answers the integrated authentication challenge with the domain-qualified
credential and the application accepts it. The allowlist launch argument
recorded under Phase 9 is not needed for that.

Getting there took the corporate root installed twice, into two stores that know
nothing of each other. The system store satisfies `curl`, `git` and the package
tooling. The browser keeps its own, and while that one is empty the application
serves its document and refuses its stylesheets and scripts. That presents as a
bare page reporting its table plugin missing, which looks nothing like a
certificate problem:

```bash
mkdir -p ~/.pki/nssdb
certutil -d sql:$HOME/.pki/nssdb -N --empty-password 2>/dev/null
certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n "NYS-ITS-Root-R1" \
  -i /usr/local/share/ca-certificates/nysits-root.crt
certutil -d sql:$HOME/.pki/nssdb -L
```

Next is Phase 8, registering the runner, and then the repository work carried by
issues 1527, 1528 and 1529.

### Four certificate stores, not one

Each of these is separate, and a root installed in one is invisible to the
others. This accounts for several failures here that looked unrelated to each
other:

| Store | What reads it |
| --- | --- |
| `/usr/local/share/ca-certificates` plus `update-ca-certificates` | `curl`, `git`, `snap`, the package tooling |
| `NODE_EXTRA_CA_CERTS` | Node, which carries its own roots |
| `~/.pki/nssdb` | Chromium, and so the browser a run drives |
| A confined application's own profile | that application alone |

`NODE_EXTRA_CA_CERTS` in `/etc/environment`, which Phase 3 writes, is read by login
sessions. The runner is a `systemd` service rather than a login session, so the Node
actions it runs never see that variable. Node reads the system store for an action only
when `NODE_OPTIONS=--use-system-ca` is set, so `release.yml` and `consumer-pr-check.yml`
set it. An action that reaches GitHub through the inspecting proxy then verifies the
corporate root the way `git` and `gh` do.

Firefox keeps a fifth, inside its profile, and on Linux it reads nothing from the
system store whatever `security.enterprise_roots.enabled` says. The profile lives
under the confined application's own tree, and Firefox holds the database open, so
it has to be closed for the write to take:

```bash
PROF=$(ls -d ~/snap/firefox/common/.mozilla/firefox/*.default* | head -1)
certutil -d sql:"$PROF" -A -t "C,," -n "NYS-ITS-Root-R1" \
  -i /usr/local/share/ca-certificates/nysits-root.crt
```

### Two environment files

The home directory copy and the one inside the checkout are separate files, and
only the one in the checkout is read by a run.

```bash
grep -H '^DB_ORACLE_PATH' ~/PlaywrightTesting/.env ~/.env
```

### Driving the guest

Over SSH from the host. Commands copied out of a chat client pick up a stray
leading character, which a round trip through a plain text editor removes. A
headed run needs a terminal on the guest's own desktop, since an SSH session has
no display; the desktop is reached over remote login rather than the console,
covered under Phase 1.

## Target

Ubuntu 26.04.1 LTS guest under Hyper-V on the work laptop, 8 vCPU, 16 GB, 100 GB
dynamic disk, registered as a self-hosted runner with the label `Linux`.

The Windows runners stay registered and stay in the pool throughout. Every
workflow keeps asking for `Windows` until issue 1529 flips the label, one
project at a time, behind a green suite.

## What the guest has to satisfy

Read off the repository rather than assumed:

- Playwright 1.63.0, matching `@playwright/test` in `package.json`.
- `package.json` carries an `engines` block asking for Node
  `^20.19.0 || ^22.13.0 || >=24` and npm `>=10`, the tightest requirement any
  dependency states. No `.nvmrc` or `volta` pin exists, so the exact patch
  version comes from whatever each runner has installed. The
  `Run Playwright tests` step prints it, so read it from a recent run.
- `oracledb` runs in thick mode (`src/_base/fixtures/SQLConnectionManager.ts:102`
  and `src/DX/fixtures/DXSQLConnectionManager.ts:45`), so the guest needs Oracle
  Instant Client and `libaio`.
- `DB_ORACLE_PATH` already comes from the environment
  (`SQLConnectionManager.ts:82`), so the guest needs a different value, not a
  code change. `.env.example:178` carries the Windows form.
- Around 110 keys live in `.env`, including `OCFS_PASSWORD`, four
  `TEST_PASSWORD_*` values, the DX OAuth2 client secret, and the AIMS and BCA
  database passwords.

## Phase 0: blockers

Status: **cleared 2026-09-01**

Three things that can end the project. Clear all three before creating a guest.

### Virtualization

Confirmed 2026-09-01 on the host: Windows 10 Enterprise.
`HypervisorPresent` reads `True`, the `vmms` service is absent, `Get-VM` does
not resolve, and all three relevant optional features read `Disabled`:

| Feature | State |
| --- | --- |
| `Microsoft-Hyper-V-All` | Disabled |
| `VirtualMachinePlatform` | Disabled |
| `Microsoft-Windows-Subsystem-Linux` | Disabled |

A hypervisor therefore runs underneath Windows with no virtualization feature
installed at all, which is Virtualization-Based Security holding it for
Credential Guard. Enterprise policy commonly turns that on. The firmware side is
settled by it: virtualization extensions are enabled and working.

The feature was enabled from an elevated prompt on 2026-09-01 and the host
rebooted for it:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -All
```

Hyper-V and Credential Guard coexist, so this does not disturb the security
policy. Confirm the role came up before creating a guest:

```powershell
Get-Service vmms | Select-Object Name,Status
Get-VMSwitch | Select-Object Name,SwitchType
```

Confirmed after the reboot: `Get-VMSwitch` returns a `Default Switch` of type
`Internal`. That cmdlet ships with the role and the switch exists only because
the service created it at startup, so the role is up and Phase 1 can start.

Run those two commands separately. Piped into one paste, the second result
renders against the first table's header and the `Status` column drops.

WSL2 is not a lower-privilege alternative here. It needs `VirtualMachinePlatform`
and `Microsoft-Windows-Subsystem-Linux`, both of which read `Disabled`, so it
asks for the same class of permission as Hyper-V while giving up snapshots, a
fixed memory ceiling, and stable network addressing across host reboots. Hyper-V
is the choice while both require the same approval.

To re-read the feature states:

```powershell
Get-WindowsOptionalFeature -Online |
  Where-Object FeatureName -match 'Hyper-V-All|VirtualMachinePlatform|Subsystem-Linux' |
  Select-Object FeatureName,State
```

`-FeatureName` binds a single string, so the names go through `Where-Object`
rather than as a list. The call needs an elevated prompt.

### Host memory

Confirmed 2026-09-01: 32 GB on the host. A 16 GB guest leaves the host half the
machine while it keeps running the Windows runners, which is comfortable.

Give the guest static memory rather than dynamic. A balloon driver reclaiming
pages under a browser run produces timeouts that read as spec flake.

### Credential sign-off

Cleared 2026-09-01. The OCFS service accounts belong to the person running this
build, so the approval is his to give and is given.

The guest still gets its own copy of `.env`, holding the OCFS password, the four
test account passwords, the DX OAuth2 client secret, and two database passwords.
Keep the file at mode 600 owned by the runner user, and treat the disk image as
carrying those secrets: an exported `.vhdx` carries the whole file with it.

## Phase 1: create the guest

Status: **done 2026-09-01**

Use the current Ubuntu LTS **Desktop** image, not Server. Phase 9 runs the login
spike headed and watched, and the suite walk needs the same whenever a Linux
rendering difference has to be seen rather than inferred. A Server install has
no display, so headed there means a virtual framebuffer and screenshots.

Installed 2026-09-01: Ubuntu 26.04.1 LTS, kernel 7.0.0-30-generic.

Host disk headroom, confirmed 2026-09-01: 139.3 GB free of 475 GB. The 100 GB
below is a dynamic disk, so it starts near zero and grows with use. Ubuntu
Desktop plus Node, the browsers, and Instant Client settles around 15 to 20 GB,
which the host carries comfortably.

Download the image and note where it lands. Then, from
an elevated prompt:

```powershell
New-VM -Name pw-linux-runner -Generation 2 -MemoryStartupBytes 16GB `
  -NewVHDPath "C:\VMs\pw-linux-runner.vhdx" -NewVHDSizeBytes 100GB `
  -SwitchName "Default Switch"
Set-VM -Name pw-linux-runner -ProcessorCount 8 -StaticMemory `
  -AutomaticCheckpointsEnabled $false
Set-VMFirmware -VMName pw-linux-runner `
  -SecureBootTemplate MicrosoftUEFICertificateAuthority
Add-VMDvdDrive -VMName pw-linux-runner -Path "C:\ISOs\<ubuntu-desktop>.iso"
Set-VMFirmware -VMName pw-linux-runner `
  -FirstBootDevice (Get-VMDvdDrive -VMName pw-linux-runner)
Start-VM -Name pw-linux-runner
vmconnect.exe localhost pw-linux-runner
```

Four of those settings are load-bearing:

- The Secure Boot template. The default Windows template refuses to boot Ubuntu.
- `-StaticMemory`. A balloon driver reclaiming pages under a browser run
  produces timeouts that read as spec flake.
- `Default Switch`, which is network address translation behind the host. An
  external switch puts a second hardware address on the corporate network, which
  network access control usually quarantines.
- Automatic checkpoints off. They accumulate disk on a machine writing traces.

### Choices during the install

- **Minimal installation.** The office suite, games, and media tools are dead
  weight on a machine that runs a test suite.
- **Skip third-party drivers.** Hyper-V presents synthetic devices and the
  drivers for them are already in the kernel.
- **Erase disk and install.** The disk is the virtual one created above.
- **The username becomes the runner account.** It owns the checkout, the
  `.env`, and the mounted share, and it is the name passed to `svc.sh install`
  in Phase 8. Pick one worth keeping.
- **Leave automatic login off.** The runner runs as a service and needs no
  desktop session.

### After first boot

Install an SSH server, so the rest of the build is driven from a terminal on the
host rather than typed into the Hyper-V console:

```bash
sudo apt-get update && sudo apt-get install -y openssh-server
ip -4 addr show scope global | grep inet
```

The Default Switch hands out a new address range after a host reboot, so read
the address when you need it rather than pinning it anywhere.

After the install finishes, drop the installer media so the guest stops booting
into it:

```powershell
Set-VMDvdDrive -VMName pw-linux-runner -Path $null
```

### Desktop access

The Hyper-V console opens at a fixed low resolution and shares no clipboard with
the host, so the desktop is reached over the network instead.

Enhanced session mode is not available here and cannot be made available, for
two independent reasons. The host client never offers the connection dialog and
keeps its own menu entry grayed out, with every requirement in place, so nothing
ever reaches the guest. Underneath that, the feature is `xrdp` reached over a
hypervisor socket, and `xrdp` serves an X11 desktop, which this release does not
have:

```bash
ls /usr/share/xsessions/         # No such file or directory
ls /usr/share/wayland-sessions/  # ubuntu.desktop
```

GNOME dropped X11 support upstream, so the guest's only session is Wayland.
`xrdp` with `xorgxrdp` starts an X server, GNOME starts against it, finds no
session it can run, and stops. The signature is a clean exit rather than a
crash, which reads as a configuration fault and is not one:

```
[INFO ] X server :10 is working
[INFO ] Session in progress on display :10. Waiting until the window manager ...
[WARN ] Window manager (pid N, display 10) exited quickly (1 secs).
```

The user journal for that moment reaches `gnome-session-shutdown.target` in
order and names nothing that failed to start. Every desktop that needs X11 ends
the same way here, so keeping `xrdp` means running a window manager that is not
the one the guest already has.

GNOME's own remote desktop serves the Wayland session directly and negotiates
the client's resolution, so a 4K panel gets 4K and the clipboard carries. It
wants the same port, so `xrdp` goes first:

```bash
sudo systemctl disable --now xrdp xrdp-sesman
sudo apt-get install -y gnome-remote-desktop
```

The settings panel generates the certificate the daemon requires. Driven from a
terminal it is made by hand, and owned by the account the system service runs
as:

```bash
sudo mkdir -p /etc/gnome-remote-desktop
sudo openssl req -x509 -newkey rsa:4096 -nodes -days 3650 \
  -keyout /etc/gnome-remote-desktop/rdp-tls.key \
  -out /etc/gnome-remote-desktop/rdp-tls.crt \
  -subj "/CN=<guest-hostname>"
sudo chown gnome-remote-desktop:gnome-remote-desktop \
  /etc/gnome-remote-desktop/rdp-tls.key /etc/gnome-remote-desktop/rdp-tls.crt
sudo chmod 600 /etc/gnome-remote-desktop/rdp-tls.key
```

```bash
sudo grdctl --system rdp set-tls-cert /etc/gnome-remote-desktop/rdp-tls.crt
sudo grdctl --system rdp set-tls-key /etc/gnome-remote-desktop/rdp-tls.key
sudo grdctl --system rdp set-credentials
sudo grdctl --system rdp enable
sudo systemctl enable --now gnome-remote-desktop.service
sudo grdctl --system status
ss -ltn | grep 3389
```

`set-credentials` prompts for the pair rather than taking them as arguments, so
they stay out of shell history.

From the host, against the guest's fixed address on the internal switch:

```powershell
mstsc /v:192.168.220.10
```

Two credential prompts, and they are different things. The first belongs to the
remote desktop layer and takes the pair set above. The second is the greeter,
and takes the guest account. The certificate is self-signed, so the client warns
once.

A user who already holds a session is refused a second one without saying so,
so log the console out before connecting.

## Phase 2: network reachability

Status: **passed 2026-09-01**

Everything downstream is wasted effort if the guest cannot reach what the suite
needs. Prove it before installing anything else.

### Tools the checks need

Ubuntu Desktop ships neither of these:

```bash
sudo apt-get install -y netcat-openbsd curl
```

### Getting .env onto the guest

From a terminal on the Windows host, using the address the guest reported after
its first boot. The Windows OpenSSH client provides `scp`:

```powershell
scp C:\path\to\.env <runner-user>@<guest-address>:/home/<runner-user>/.env
```

Then lock it down on the guest, because it carries the OCFS password, the four
test account passwords, the DX OAuth2 client secret, and two database passwords:

```bash
chmod 600 ~/.env
```

### The checks

```bash
set -a; . ~/.env; set +a
getent hosts "$(echo "$CCA_BASE_URL" | sed -E 's#https?://([^/:]+).*#\1#')"
curl -sS -o /dev/null -w '%{http_code}\n' "$CCA_BASE_URL"
nc -zv "$(echo "$DB_CONNECTION_STRING" | sed -E 's#.*//([^:/]+).*#\1#')" 1521
nc -zv ocfs-smb 445
curl -sS -o /dev/null -w '%{http_code}\n' https://github.com
```

Sourcing the file assumes every value is shell-safe. If it errors, read the one
value the failing check needs with `grep '^CCA_BASE_URL=' ~/.env` rather than
editing the file to suit the shell.

### What the guest sits behind

Confirmed 2026-09-01 on the host: `vEthernet (Default Switch)` is up at
`172.30.48.1`, so the guest takes a lease in `172.30.48.0/20` with that address
as both its gateway and its name server. The switch forwards name lookups to
whatever the host resolves with.

The host reaches the corporate network over Wi-Fi, its wired adapters sitting on
link-local addresses. The guest inherits that path, so it reaches the
application and the databases only as well as the host's own connection does.

The installer's network page can leave its Next button disabled while the
interface is still coming up. Skipping the step costs nothing: a minimal install
with third-party drivers skipped needs no network.

### The Default Switch serves no leases here

Established 2026-09-01. The guest's `eth0` comes up with `LOWER_UP` and a MAC
matching the adapter the host reports, then takes a `169.254.0.0/16` address,
which Linux assigns only when DHCP goes unanswered. The lease allocator behind
the Default Switch is the Internet Connection Sharing service, which reports
Running but refuses to stop or restart on this host.

Routing and address translation are unaffected. With an address and a route set
by hand, the guest reaches the wider network. The host's own gateway address
does not answer ping, which is Windows Firewall dropping inbound ICMP rather
than a routing failure, so a timeout against it proves nothing either way. Test
the path with a destination beyond the host instead.

Configure the address through NetworkManager rather than with `ip addr add`.
An address added by hand works for traffic and leaves NetworkManager still
believing the interface has only the address DHCP failed to replace, so anything
asking it for connectivity is told there is none. The connection is named for
the netplan file that created it:

```bash
nmcli con show
sudo nmcli con mod "netplan-eth0" ipv4.method manual \
  ipv4.addresses 172.30.48.100/20 ipv4.gateway 172.30.48.1 \
  ipv4.dns "10.108.43.7,10.108.43.8"
sudo nmcli con up "netplan-eth0"
```

`nmcli networking connectivity` then reports `full`, and the address survives a
reboot.

The permanent answer is a dedicated internal switch carrying its own address
translation, which owes nothing to the sharing service and holds a fixed subnet:

```powershell
New-VMSwitch -SwitchName "pw-nat" -SwitchType Internal
New-NetIPAddress -IPAddress 192.168.220.1 -PrefixLength 24 `
  -InterfaceAlias "vEthernet (pw-nat)"
New-NetNat -Name "pw-nat" -InternalIPInterfaceAddressPrefix 192.168.220.0/24
Connect-VMNetworkAdapter -VMName pw-linux-runner -SwitchName "pw-nat"
```

The guest then holds a static address on that subnet, which is what a runner
wants: the same address after every reboot, so anything pointing at it keeps
working. The Default Switch re-randomizes its subnet on each host reboot and
cannot offer that.

### The guest has no network over the VPN

Established 2026-09-02. The guest reaches everything it needs while the host is
on the corporate network directly. While the host is connected through Cisco
AnyConnect from home, nothing the guest sends leaves the host.

The virtualization side is not the cause, and was verified end to end:

| Checked | State |
| --- | --- |
| Switch, address, and NAT rule | present, `Active: True` |
| `Forwarding` on the host interface | `Enabled` |
| `WinNat` service | `Running`, `Automatic` |
| Network category of the interface | `Private` |
| The machine's adapter | one, attached to the switch |
| Address resolution for the gateway | `REACHABLE` |
| Firewall inside the guest | inactive |

Address resolution reaching the host while nothing routes past it places the
loss above the link and outside anything configurable here. Every network
component bound to the interface is Microsoft's own, so the filter responsible
sits lower in the stack. The client's own preferences pane is empty, its profile
having locked every setting, so there is no switch on this side to throw.

Traffic from the machine is forwarded rather than locally generated, and a
tunnel-all client drops exactly that. The Windows runners are unaffected because
they run on the host, where their traffic originates locally.

The consequence is an operating constraint rather than a defect: **the guest is
available while the host is on the corporate network, and dormant while the host
is tunneling.** Lifting it means a profile change permitting forwarded traffic
from this subnet, which is the network team's to make, or hosting the runner
somewhere that is not behind a per-user tunnel.

The gateway not answering a ping is unrelated and means nothing. The host
declines inbound echo requests on that interface whether traffic flows or not,
so a timeout there is never evidence either way.

### Resolvers

The corporate name servers are `10.108.43.7` and `10.108.43.8`. A plain address
translation rule forwards no name lookups, unlike the Default Switch, so the
guest is pointed at those two directly. It has to resolve the application host,
the database host, and the share, and only the corporate servers carry them.

### What it answered

Every endpoint the suite needs is reachable from the guest:

| Target | Host | Port | Result |
| --- | --- | --- | --- |
| CCA | `cnuat.ocfs.ny.gov` | 443 | open |
| DX | `api-qa.ny.gov` | 443 | open |
| Oracle | `vscfs001.svc.ny.gov` | 1535 | open |
| Share | `ocfs-smb` | 445 | open |

`ocfs-smb` resolves as a short name with no search suffix configured, so the
guest needs only the two corporate name servers.

`DB_CONNECTION_STRING` holds a full descriptor rather than an Easy Connect
string, so the host and port are inside it: `vscfs001.svc.ny.gov` on 1535,
service `CONUA`. A naive split on `//` returns the whole descriptor and tests
nothing.

### Line endings

A `.env` copied from the Windows side carries CRLF. Sourcing it in a shell puts
a trailing carriage return on every value, which resolves hostnames correctly
and then fails anything stricter: a URL built from one is rejected as malformed.
Blank lines become a lone carriage return the shell tries to run, and the return
rewinds the cursor, so the errors print as a bare `: command not found` with no
clue what produced them.

```bash
sed -i 's/\r$//' ~/.env && chmod 600 ~/.env
```

Node reads either form, so only shell use needs this.

### Reading the results

Name resolution is the usual failure. Behind address translation the guest picks
up the host resolver but not the corporate search suffix, so an internal short
name resolves on the host and fails in the guest. Set `Domains=` in
`/etc/systemd/resolved.conf` to the suffix the laptop uses rather than pinning
addresses.

A certificate error belongs to Phase 3 and is expected here, since the corporate
root is not trusted yet. A refused connection or an unknown host belongs to this
phase and stops it.

## Phase 3: corporate certificate chain

Status: **done 2026-09-01**

The network inspects TLS selectively. An inspected host presents a certificate
signed by a private authority, and a guest that does not carry that authority
refuses the connection with `unable to get local issuer certificate`. An
uninspected host presents its real certificate and verifies against the stock
bundle.

Established 2026-09-01. Inspected: `github.com`, `snapcraft.io`, and
`archive.ubuntu.com` over TLS. Not inspected: `registry.npmjs.org` and
`packages.microsoft.com`, both of which verify as they stand. The application
host is not inspected either, so it verified before any of this was done and
gave a false impression that the phase could be skipped.

Package installs work throughout because the archives are read over plain HTTP
with signed packages, so `apt` never presents the problem that everything else
does.

The chain on an inspected host runs leaf, then `A1K01NYXFW1-CA.svc.ny.gov`, then
`New York State ITS Intranet CA1`, then
`New York State ITS Private Root Authority R1`. The server sends every link
except the last, so the root is what has to be added.

Export it from the Windows side, where it is already trusted:

```powershell
$c = Get-ChildItem Cert:\LocalMachine\Root |
  Where-Object { $_.Subject -match 'ITS Private Root Authority R1' } |
  Select-Object -First 1
$pem = "-----BEGIN CERTIFICATE-----`n" +
  [Convert]::ToBase64String($c.RawData,'InsertLineBreaks') +
  "`n-----END CERTIFICATE-----`n"
Set-Content -Path C:\temp\nysits-root.crt -Value $pem -Encoding ascii
```

Install it on the guest. The `.crt` extension and the PEM encoding are both
required, and anything else is ignored without a word:

```bash
sudo cp /tmp/nysits-root.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

Node carries its own roots rather than reading the system store, so it is told
separately. This matters for the browser downloads and for any package fetch:

```bash
echo 'NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/nysits-root.crt' |
  sudo tee -a /etc/environment
```

Verify against a host known to be inspected, not against the application:

```bash
curl -sSI https://github.com | head -1
```

Both `github.com` and `snapcraft.io` answer `HTTP/2 200` once the authority is
in place, where each refused before it.

`update-ca-certificates` reports `rehash: warning: skipping ca-certificates.crt,
it does not contain exactly one certificate or CRL`. That names the aggregate
bundle it just wrote and is not a failure. The line that matters beside it is
`1 added, 0 removed`.

Write the Node variable without a pipe. A pipeline split across two lines leaves
`tee` waiting on input that never comes, and the shell offers no clue that is
what happened:

```bash
sudo sh -c 'echo NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/nysits-root.crt >> /etc/environment'
```

## Phase 4: Node and dependencies

Status: **done 2026-09-01**

The guest runs Node 22.22.1 against 22.15.1 on the Windows runners. The major
matches, so the native module interface does, and each machine builds its own
`node_modules`. Only the `engines` block bounds the version, so the patch
levels drift between the two machines.

Read the version off a recent run before installing anything. Then clone and
`npm ci` on the guest. The native `oracledb` binding builds against the guest,
so it cannot be shared with the host.

### npm has to come up separately

Ubuntu ships npm as its own package, held at 9.2.0, while Node 22 expects the
npm 10 series. Installing `nodejs` alone therefore leaves a pair that
`@faker-js/faker` and the `engines` block both refuse, and `npm ci` opens every
run with `npm WARN EBADENGINE`. Nothing fails on the warning, and the suite
still runs.

Put a newer npm in `/usr/local`, which comes ahead of the distribution copy in
`/usr/bin` on `PATH`:

```bash
sudo npm install -g npm@10
```

Then confirm the pair, from a fresh shell so the new `PATH` entry resolves:

```bash
node -v && npm -v
```

## Phase 5: Oracle Instant Client

Status: **done 2026-09-01**

`oracleClientVersionString` reports `23.26.2.0.0`.

Match the major version already on the Windows runner, readable from its
`C:\Oracle\instantclient` folder.

Release 23.26 is what the current archive unpacks, into
`/opt/oracle/instantclient_23_26`.

`oracledb` opens `libaio.so.1`, and 26.04 ships that library as `libaio1t64`,
which installs `libaio.so.1t64` and no plain `libaio.so.1`, so the link is
needed. Confirm rather than assume, since the name moves between releases:

```bash
apt-cache search libaio
dpkg -L <the package it names> | grep 'libaio.so'
```

Then install it, and symlink whatever it installed to the name `oracledb` opens
if the two differ:

```bash
sudo apt-get install -y <libaio package> unzip
sudo mkdir -p /opt/oracle
sudo unzip -q instantclient-basiclite-linux.x64-*.zip -d /opt/oracle
```

A `libaio.so.1` that is already present needs no link. If the installed file is
`libaio.so.1t64`, link it:

```bash
sudo ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 \
  /usr/lib/x86_64-linux-gnu/libaio.so.1
```

Register the directory with the dynamic linker. Handing `initOracleClient` a
`libDir` locates `libclntsh.so` and nothing else, so its siblings in the same
directory fail to load and the error names one of them rather than the
directory. Use `ldconfig` rather than `LD_LIBRARY_PATH`: the runner executes as
a service and inherits nothing from a shell profile, so a variable that makes
this work by hand leaves the service failing for a reason that looks unrelated.

```bash
sudo sh -c 'echo /opt/oracle/instantclient_23_26 > /etc/ld.so.conf.d/oracle-instantclient.conf'
sudo ldconfig && ldconfig -p | grep -E 'libclntsh|libnnz'
```

Set `DB_ORACLE_PATH=/opt/oracle/instantclient_<version>` in the guest `.env`,
then prove it:

```bash
node -e "const o=require('oracledb');o.initOracleClient({libDir:process.env.DB_ORACLE_PATH});console.log(o.oracleClientVersionString)"
```

## Phase 6: artifact share mount

Status: **done 2026-09-08**

The guest mounts `//ocfs-smb.svc.ny.gov/ocfs_home` at `/mnt/ocfs_home` through
`/etc/fstab`, so the artifact root `/mnt/ocfs_home/it5677/pw-artifacts` is
reachable and both `save-artifacts.sh` and `read-artifacts.sh` work there.

`scripts/README-artifact-share.md` carries the working recipe and is the copy
to follow. Two details in it are what the mount turns on: the short name
`ocfs-smb` does not resolve on the guest, which carries no search domain and
cannot reach the corporate resolver, so `/etc/hosts` pins
`ocfs-smb.svc.ny.gov` to 10.108.26.101; and the credentials file the mount
reads is `/etc/ocfs-share.cred`.

`nofail` keeps a share outage from holding the guest at boot. Artifact capture
is best-effort by design, so it must never be able to block the machine.

## Phase 7: browsers

Status: **done 2026-09-01**

A launched and closed browser is the check that counts, and it passes.

```bash
npx playwright install-deps chromium firefox
npx playwright install chromium firefox
```

`install-deps` belongs to the guest build and stays out of the per-job script,
which installs only the one browser the dispatched project needs.

Playwright maps `install-deps` against a list of releases it knows, and 26.04 is
newer than the list this version carries, so the command may refuse the
distribution outright. That is survivable: a Desktop install already carries most
of what the browsers link against. If it refuses, install the browsers anyway and
let the browser itself report what is missing:

```bash
npx playwright install chromium firefox
node -e "require('playwright').chromium.launch().then(b=>b.close())"
```

A launch that succeeds needs nothing further. One that fails names the missing
library, which `apt-file search` resolves to a package.

## Phase 8: register the runner

Status: **done 2026-09-03, three instances**

Runners register on the `merph518` organization, in its Default group. The
group layout, the labels each runner carries, and the move from repository
registration are in [RunnerRegistration.md](RunnerRegistration.md).

A registration token is a one-time credential taken from the organization's
runner settings page, or minted with `gh api -X POST
orgs/merph518/actions/runners/registration-token`, which needs `admin:org`. It does
not go in a file, a commit, or a chat message, and it is only good for about an
hour.

### One guest, several runners

A single self-hosted runner service processes one job at a time, so getting
concurrent jobs onto this guest means registering several runner instances
rather than raising a Playwright worker count. Each instance is its own
directory, holding its own `.runner` and `.credentials` files and its own
`systemd` service, all pointed at the same repository under the same label:

```bash
mkdir -p ~/runner-pkg && cd ~/runner-pkg
curl -o runner.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.337.0/actions-runner-linux-x64-2.337.0.tar.gz

TOKEN=$(gh api -X POST \
  orgs/merph518/actions/runners/registration-token \
  --jq .token)
for i in 1 2 3; do  # 4 5 6 for the second set
  mkdir -p ~/actions-runner-$i
  tar xzf ~/runner-pkg/runner.tar.gz -C ~/actions-runner-$i
  cd ~/actions-runner-$i
  ./config.sh --url https://github.com/merph518 --runnergroup Default \
    --token "$TOKEN" --labels playwright --name pw-linux-runner-$i --unattended
  sudo ./svc.sh install mfagerstrom
  sudo ./svc.sh start
  cd ~
done
```

`svc.sh` reads its state relative to the current directory rather than its own
path, so checking or restarting one has to run with that instance's directory as
the working directory, not by invoking the script from outside it:

```bash
cd ~/actions-runner-2 && sudo ./svc.sh status
```

The registered set is visible to a token with `admin:org`:

```bash
gh api orgs/merph518/actions/runners \
  --jq '.runners[] | "\(.name)  \(.status)  \([.labels[].name] | join(","))"'
```

Adding instances is the same loop with a new range; the mint at the top of
the loop gives each set its own token. The
guest's 8 vCPU and 16 GB bound how many browser jobs it carries at once: a
headless Chromium job with a trace wants roughly 2 GB, so six instances call
for the static allocation raised toward 24 GB in Hyper-V, which the 32 GB host
can spare. Read `free -g` under a full pool before trusting the sixth.

The guest reports 15 GB with six instances registered, and full sweeps on all
six have run it out of memory: the kernel's global killer ended a `node`
process of 2 to 4 GB, and systemd then stopped that runner's service, taking
the runner offline. `Runner Memory Limit (on demand)` caps each service with a
drop-in (`MemoryMax` and `OOMPolicy=continue`), sized as the guest's memory
less a reserve, split evenly across the services.
The caps add up to less than the guest has, so a job that overruns is killed
inside its own service and that runner stays online for the next job. At
15 GB the share is about 2.2 GB, below the largest jobs seen, so those jobs
still fail; raising the guest toward 24 GB is what lets them finish, and
running `apply` again after the raise resizes the cap. `report` prints each
service's peak memory and kill count without changing anything.

The Windows runners stay registered. The pool holds both while the suites are
validated.

### What one instance running a browser project still cannot do

Registering more runners raises how many jobs run at once; it says nothing
about a single job's own `--workers` value. `scripts/build-changed-spec-matrix.sh`
holds every browser project, CCA and MR alike, at one worker, because a job
drives one real session against one leased account and one CONNECTIONS login.
Raising that number does not gain concurrency, since one job only holds one
lease regardless of how many workers read it; it would put several workers
against the one login the job already has, which is the kind of session-state
collision already seen when two separate jobs end up sharing a worker. The DX
projects run two workers today because they carry no browser session to
collide over. Neither number is a hardware ceiling; both are set by what the
job is holding, and stay put regardless of how many instances the guest
carries.

### What the workspace needs

A job runs out of that instance's `_work/PlaywrightTesting/PlaywrightTesting`,
not out of any checkout made by hand. Each instance has its own `_work` tree,
so each one needs its own copy. `.env` lives there, untracked, and checkout
runs with cleaning disabled so it survives between jobs. Nothing creates it, so
it is placed once the first job on that instance has made the directory:

```bash
for i in 1 2 3 4 5 6; do
  WS=~/actions-runner-$i/_work/PlaywrightTesting/PlaywrightTesting
  [ -d "$WS" ] || { echo "$i: no workspace yet"; continue; }
  cp ~/.env "$WS/.env" && sed -i 's/\r$//' "$WS/.env" && chmod 600 "$WS/.env"
  grep -H '^DB_ORACLE_PATH' "$WS/.env"
done
```

`DB_ORACLE_PATH` has to name the Instant Client directory on this machine. A
copy taken from the Windows side carries a Windows path, the driver fails to
load, and the failure names a library rather than the setting.

The service inherits no shell environment, so the Instant Client libraries have
to be resolvable from the loader cache rather than from `LD_LIBRARY_PATH` set in
a profile. Phase 5 covers that, and it is what makes the setting work under the
service as well as in a terminal.

## Phase 9: the login spike

Status: **answered 2026-09-03**

### What the application actually does

Established 2026-09-01, before any code was written.

A request to the CCA base URL answers `302` to an ADFS endpoint at
`fs.svc.ny.gov/adfs/oauth2/authorize/`, an OpenID Connect flow carrying PKCE and
`response_mode=form_post`. The certificate chain is trusted by the guest's stock
bundle, so no certificate work is needed to reach it.

The suite authenticates by handing the browser context a domain-qualified
credential, `SVC\<user>`, at `src/_base/fixtures/User.ts:124`, which is the
shape Windows Integrated Authentication takes rather than Basic. A response
handler alongside it logs `www-authenticate` on any 401.

The same request under a Linux user agent and under a Windows one produces an
identical chain, so the endpoint is not choosing by user agent:

```
302  cnuat.ocfs.ny.gov  ->  fs.svc.ny.gov/adfs/oauth2/authorize/
302                     ->  fs.svc.ny.gov/adfs/oauth2/authorize/wia
401  WWW-Authenticate: Negotiate
     WWW-Authenticate: NTLM
```

Every client is routed to the integrated authentication endpoint and challenged
there. No login form is offered to anyone, which is why the fixture answers with
a domain-qualified credential rather than filling one.

A browser on this guest answers that challenge. A spec run reaches
`cnuat.ocfs.ny.gov/conxcomp` with the impersonated worker's name rendered in the
header, so the handshake completes and the application accepts the session. This
is the finding the migration turned on, and it clears the way for the browser
suites.

Chromium keeps an allowlist of hosts it will perform integrated authentication
against, supplied by `--auth-server-allowlist`. It is not needed here.

What remains is the page arriving without its scripts or its styling, reported
as `TypeError: $(...).DataTable is not a function`. jQuery runs, so this is
assets failing to load rather than a browser unable to execute them. The browser
reads a certificate database of its own, covered under the resume note above.

The check that decides whether the migration proceeds. Run it by hand on the
guest, headed, watching it, before any of the three issues gets a line of code.

```bash
npx playwright test <a cca login spec> --project=cca.chromium --headed --workers=1
```

If login stalls on an authentication prompt no spec fills in, that is Windows
integrated authentication, and it cannot be ported. The migration stops there
and the three issues close unstarted.

Everything before this phase is recoverable setup. This phase returns a verdict.

## Open questions

Carry these until each one is answered here.

- Does CCA render fully on Linux Chromium? Login works and the application
  accepts the impersonated worker, but the page arrives unstyled and jQuery
  reports its table plugin missing, so some of its assets are not loading.
- Does `mr.firefox` hold up on Linux Firefox? Different timing and rendering
  profile, and the suite already carries a modal dismiss quirk on Windows.
- Which assertions read a formatted date or a locale-sensitive string? Those
  differ across the two platforms and will surface as failures that look
  unrelated to the move.
- Which Oracle Instant Client major version do the Windows runners use?
- Which Node version do the Windows runners use?
