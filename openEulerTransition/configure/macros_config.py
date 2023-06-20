import os

RPM_SYSTEM_MACROS = {
    "%package_help": "%package help" + os.linesep +
                     "Summary: Documents for %{name}" + os.linesep +
                     "BuildArch: noarch" + os.linesep +
                     "Requires: man info" + os.linesep +
                     "%description help" + os.linesep +
                     "Man pages and other related documents for %{name}." + os.linesep,
    "%{?systemd_requires}": "Requires(post): systemd" + os.linesep +
                            "Requires(preun): systemd" + os.linesep +
                            "Requires(postun): systemd" + os.linesep,
    "%{?systemd_ordering}": "OrderWithRequires(post): systemd" + os.linesep +
                            "OrderWithRequires(preun): systemd" + os.linesep +
                            "OrderWithRequires(postun): systemd",
}
