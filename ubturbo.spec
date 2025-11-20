%global version    1.0.0
%global release_version 1
%global __strip /bin/true

Name:          ubturbo
Version:       %{version}
Release:       %{release_version}
Summary:       Huawei ubturbo
License:       GPLv2
URL:           https://support.huawei.com
Source0:       ubturbo.tar.gz
Provides:      %{name}
Vendor:        Huawei Technologies Co., Ltd.
BuildRoot:     %{buildroot}
ExclusiveArch: %arm64
BuildRequires: kernel-devel >= 5.10.0-136.12.0.86 make >= 4.3 gcc >= 10.3.1 cmake libvirt libvirt-devel
BuildRequires: libboundscheck
BuildRequires: make
BuildRequires: gcc flex bison elfutils-libelf-devel openssl openssl-devel ncurses-devel dwarves 
BuildRequires: cmake
BuildRequires: chrpath
BuildRequires: patchelf
BuildRequires: libboundscheck
BuildRequires: rapidjson
BuildRequires: ninja-build
Requires:      kernel >= 5.10.0-136.12.0.86
buildArch     : aarch64 x86_64
ExclusiveArch : aarch64

%description
ubturbo

#define smap
%define debug_package %{nil}
%define smap_dir /lib/modules/smap
%define ucache_dir /lib/modules/ucache
%define smap_libsmap_dir /usr/lib64
%define udev_rules_dir %{_sysconfdir}/udev/rules.d
%define kernel_devel_version 6.6.0+

#define rmrs
%define debug_package %{nil}
%define ubturbo_dir /opt/ubturbo
%define ubturbo_bin_dir /opt/ubturbo/bin
%define ubturbo_lib_dir /opt/ubturbo/lib
%define ubturbo_conf_dir /opt/ubturbo/conf
%define ubturbo_scripts_dir /opt/ubturbo/scripts

%package smap
Summary: smap

%description smap
This package contains the Huawei SMAP Driver

%package rmrs
Summary: rmrs

%description rmrs
This package contains the Huawei os_turbo Driver

%prep
%setup -q -T -b 0 -c -n ubturbo

%build
#build smap
cd %{_builddir}
git clone https://gitee.com/src-openeuler/spdlog.git
mv spdlog/v1.11.0.tar.gz .
rm -rf %{_builddir}/spdlog
ls
pwd
tar -zxvf v1.11.0.tar.gz

cd %{_builddir}
git clone -b OLK-6.6 https://gitee.com/openeuler/kernel.git
cd kernel
make openeuler_defconfig
sed -i 's/CONFIG_MODULE_SIG_KEY=.*$/CONFIG_MODULE_SIG_KEY="certs\/signing_key.pem"/g' .config
make olddefconfig
sed -i -e '/bzip2 -9 --keep vmlinux/,+1d' scripts/package/mkspec
INSTALL_MOD_STRIP=1 make rpm-pkg -j 64 -s
cd %{_builddir}
rpm2cpio /home/lkp/rpmbuild/BUILD/kernel/rpmbuild/RPMS/aarch64/kernel-devel-6.6.0+-1.oe2403sp3.aarch64.rpm | cpio -div
cd %{_builddir}/ubturbo/plugins/smap/src/drivers && make -j`nproc` -C %{_builddir}/usr/src/kernels/6.6.0+ M=%{_builddir}/ubturbo/plugins/smap/src/drivers modules
cp %{_builddir}/ubturbo/plugins/smap/src/drivers/Module.symvers %{_builddir}/ubturbo/plugins/smap/src/tiering/depends
rm -rf %{_builddir}/ubturbo/plugins/smap/src/tiering/depends/hisi.symvers
cd %{_builddir}/ubturbo/plugins/smap/src/tiering && make -j`nproc` -C %{_builddir}/usr/src/kernels/6.6.0+ M=%{_builddir}/ubturbo/plugins/smap/src/tiering modules
cd %{_builddir}/ubturbo/plugins/smap/src/ucache && make -j`nproc` -C %{_builddir}/usr/src/kernels/6.6.0+ M=%{_builddir}/ubturbo/plugins/smap/src/ucache modules

rm -rf %{_builddir}/ubturbo/plugins/smap/3rdparty/spdlog
mv %{_builddir}/spdlog-1.11.0 %{_builddir}/spdlog
cp -rf %{_builddir}/spdlog %{_builddir}/ubturbo/plugins/smap/3rdparty
ls %{_builddir}/ubturbo/plugins/smap/3rdparty/spdlog
cd %{_builddir}/ubturbo/plugins/smap && cmake -DCMAKE_BUILD_TYPE=Release .
make -j`nproc` install

#build rmrs
cd %{_builddir}/ubturbo && bash -x build.sh -c

%install
#install smap
echo "########RPM_BUILD_ROOT=${RPM_BUILD_ROOT}"
rm -rf ${RPM_BUILD_ROOT}
mkdir -p -m755 ${RPM_BUILD_ROOT}/%{smap_dir}
mkdir -p -m755 ${RPM_BUILD_ROOT}/%{ucache_dir}
mkdir -p -m755 ${RPM_BUILD_ROOT}/%{smap_libsmap_dir}
mkdir -p -m755 ${RPM_BUILD_ROOT}/%{udev_rules_dir}
%{__install} -b -m 0500 %{_builddir}/ubturbo/plugins/smap/src/drivers/smap_tracking_core.ko ${RPM_BUILD_ROOT}/%{smap_dir}
%{__install} -b -m 0500 %{_builddir}/ubturbo/plugins/smap/src/drivers/smap_access_tracking.ko ${RPM_BUILD_ROOT}/%{smap_dir}
%{__install} -b -m 0500 %{_builddir}/ubturbo/plugins/smap/src/drivers/smap_histogram_tracking.ko ${RPM_BUILD_ROOT}/%{smap_dir}
%{__install} -b -m 0500 %{_builddir}/ubturbo/plugins/smap/src/tiering/smap_tiering.ko ${RPM_BUILD_ROOT}/%{smap_dir}
%{__install} -b -m 0500 %{_builddir}/ubturbo/plugins/smap/src/ucache/ucache.ko ${RPM_BUILD_ROOT}/%{ucache_dir}
%{__install} -b -m 0500 %{_builddir}/ubturbo/plugins/smap/output/smap/lib/libsmap.so ${RPM_BUILD_ROOT}/%{smap_libsmap_dir}
%{__install} -b -m 0640 %{_builddir}/ubturbo/plugins/smap/99-smap.rules ${RPM_BUILD_ROOT}/%{udev_rules_dir}
#install rmrs
mkdir -p -m755 ${RPM_BUILD_ROOT}/%{ubturbo_dir}
mkdir -p -m755 ${RPM_BUILD_ROOT}/%{ubturbo_bin_dir}
mkdir -p -m755 ${RPM_BUILD_ROOT}/%{ubturbo_lib_dir}
mkdir -p -m755 ${RPM_BUILD_ROOT}/%{ubturbo_conf_dir}
mkdir -p -m755 ${RPM_BUILD_ROOT}/%{ubturbo_scripts_dir}

ls %{_builddir}/ubturbo/dist
ls %{_builddir}/ubturbo/dist/release
ls %{_builddir}/ubturbo/dist/release/bin
%{__install} -b -m 0644 %{_builddir}/ubturbo/dist/release/bin/ub_turbo_exec ${RPM_BUILD_ROOT}/%{ubturbo_bin_dir}
%{__install} -b -m 0644 %{_builddir}/ubturbo/build/rpm/ubturbo.service ${RPM_BUILD_ROOT}/%{ubturbo_scripts_dir}
%{__install} -b -m 0644 %{_builddir}/ubturbo/build/rpm/cat.sh ${RPM_BUILD_ROOT}/%{ubturbo_bin_dir}
%{__install} -b -m 0644 %{_builddir}/ubturbo/dist/release/lib/libubturbo_client.so ${RPM_BUILD_ROOT}/%{ubturbo_lib_dir}
%{__install} -b -m 0644 %{_builddir}/ubturbo/dist/release/lib/librmrs_ubturbo_plugin.so ${RPM_BUILD_ROOT}/%{ubturbo_lib_dir}
%{__install} -b -m 0644 %{_builddir}/ubturbo/dist/release/conf/ubturbo_plugin_admission.conf ${RPM_BUILD_ROOT}/%{ubturbo_conf_dir}
%{__install} -b -m 0644 %{_builddir}/ubturbo/dist/release/conf/ubturbo.conf ${RPM_BUILD_ROOT}/%{ubturbo_conf_dir}
%{__install} -b -m 0644 %{_builddir}/ubturbo/dist/release/conf/plugin_rmrs.conf ${RPM_BUILD_ROOT}/%{ubturbo_conf_dir}

find ${RPM_BUILD_ROOT}/%{ubturbo_lib_dir} -name "*.so" -exec patchelf --set-rpath '$ORIGIN/../lib' {} \;
patchelf --set-rpath '$ORIGIN/../lib' ${RPM_BUILD_ROOT}/%{ubturbo_bin_dir}/ub_turbo_exec

%clean
rm -rf ${RPM_BUILD_ROOT}

%files smap
%defattr(-,ubturbo,ubturbo)
%{smap_dir}/smap_tracking_core.ko
%{smap_dir}/smap_access_tracking.ko
%{smap_dir}/smap_histogram_tracking.ko
%{smap_dir}/smap_tiering.ko
%{ucache_dir}/ucache.ko
%{smap_libsmap_dir}/libsmap.so
%{udev_rules_dir}/99-smap.rules

%files rmrs
%defattr(-,root,root)
%{ubturbo_lib_dir}/libubturbo_client.so
%{ubturbo_lib_dir}/librmrs_ubturbo_plugin.so
%{ubturbo_conf_dir}/ubturbo_plugin_admission.conf
%{ubturbo_conf_dir}/ubturbo.conf
%{ubturbo_conf_dir}/plugin_rmrs.conf
%{ubturbo_scripts_dir}/ubturbo.service
%defattr(0755,root,root,0755)
%dir %{ubturbo_bin_dir}
%{ubturbo_bin_dir}/ub_turbo_exec
%{ubturbo_bin_dir}/cat.sh

%pre smap

%post smap
cd %{smap_dir}
depmod -a
echo "external 6.6.0-* %{smap_dir}" > /etc/depmod.d/smap.conf
echo "external 6.6.0-* %{ucache_dir}" > /etc/depmod.d/ucache.conf
depmod -a

%preun smap
if [ "$1" = "0" ]; then
    modprobe -r smap_tiering
    modprobe -r smap_histogram_tracking
    modprobe -r smap_access_tracking
    modprobe -r smap_tracking_core
    modprobe -r ucache
fi

%postun smap
if [ "$1" = "0" ]; then
    rm -rf %{smap_dir}
    rm -rf %{ucache_dir}
    rm -f /etc/depmod.d/smap.conf
    rm -f /etc/depmod.d/ucache.conf
    rm -f %{udev_rules_dir}/99-smap.rules
fi
depmod -a

%pre rmrs
#!/bin/bash
# 默认日志目录和日志文件
LOG_DIR="/var/log/ubturbo"
LOG_FILE="$LOG_DIR/ubturbo-install.log"

# 检查并创建日志目录
create_log_directory() {
  # 只检查一次，减少不必要的文件系统操作
  if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR" || handle_error "Failed to create log directory $LOG_DIR"
    chmod 700 "$LOG_DIR"  # 设置日志目录权限为700
    log_message "INFO" "Log directory $LOG_DIR created successfully."
  elif [ ! -w "$LOG_DIR" ]; then
    handle_error "Log directory $LOG_DIR is not writable."
  fi
}

# 输出日志到文件和控制台
log_message() {
  local log_type="$1"
  local message="$2"

  # 获取时间戳
  local timestamp
  timestamp="$(date)"
  local log_entry="[$timestamp] [$log_type] $message"

  # 检查日志目录是否存在并且可写
  create_log_directory

  # 如果日志文件是首次创建，则设置权限为600
  if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
    chmod 600 "$LOG_FILE"  # 只在首次创建时设置权限
  fi

  # 写入日志文件
  echo "$log_entry" >> "$LOG_FILE"
}

# 统一错误处理
handle_error() {
    log_message "ERROR" "$1"
    exit 1
}

# 统一错误处理
handle_warn() {
    log_message "WARN" "$1"
}

# 调用示例：
# log_message "INFO" "This is an info message."
# log_message "ERROR" "This is an error message."
# log_message "DEBUG" "This is a debug message."

# 检查服务是否存在
service_exists() {
    local service_name="$1"
    systemctl list-units --type=service --all | grep -q "$service_name"
}

# 停止并禁用服务
stop_and_disable_service() {
    local service_name="$1"

    if service_exists "$service_name"; then
        # 停止服务
        log_message "INFO" "Stopping $service_name service..."
        if ! systemctl stop "$service_name"; then
            handle_warn "Failed to stop $service_name"
        fi

        # 禁用服务
        log_message "INFO" "Disabling $service_name service..."
        if ! systemctl disable "$service_name"; then
            handle_warn "Failed to disable $service_name"
        fi
    else
        log_message "INFO" "$service_name does not exist, skipping stop and disable."
    fi
}

# 删除文件，如果文件不存在，则跳过
remove_file_if_exists() {
    local file="$1"

    if [ -f "$file" ]; then
        log_message "INFO" "Removing file $file..."
        if ! rm -f "$file"; then
            handle_error "Failed to remove $file"
        fi
    else
        log_message "INFO" "File $file does not exist, skipping removal."
    fi
}

# 主流程
main() {
# 脚本开始执行
log_message "INFO" "======================"
log_message "INFO" "pre_install.sh started"
log_message "INFO" "======================"

# 停止并禁用服务
stop_and_disable_service "ubturbo.service"
rm -f /tmp/ubturbo_ipc

# 脚本结束执行
log_message "INFO" "======================"
log_message "INFO" "pre_install.sh ended"
log_message "INFO" "======================"
}

# 执行主流程
main "$@"

%post rmrs
#!/bin/bash

# 默认日志目录和日志文件
LOG_DIR="/var/log/ubturbo"
LOG_FILE="$LOG_DIR/ubturbo-install.log"

# 检查并创建日志目录
create_log_directory() {
  # 只检查一次，减少不必要的文件系统操作
  if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR" || handle_error "Failed to create log directory $LOG_DIR"
    chmod 700 "$LOG_DIR"  # 设置日志目录权限为700
    log_message "INFO" "Log directory $LOG_DIR created successfully."
  elif [ ! -w "$LOG_DIR" ]; then
    handle_error "Log directory $LOG_DIR is not writable."
  fi
}

# 输出日志到文件和控制台
log_message() {
  local log_type="$1"
  local message="$2"

  # 获取时间戳
  local timestamp
  timestamp="$(date)"
  local log_entry="[$timestamp] [$log_type] $message"

  # 检查日志目录是否存在并且可写
  create_log_directory

  # 如果日志文件是首次创建，则设置权限为600
  if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
    chmod 600 "$LOG_FILE"  # 只在首次创建时设置权限
  fi

  # 写入日志文件
  echo "$log_entry" >> "$LOG_FILE"
}

# 统一错误处理
handle_error() {
    log_message "ERROR" "$1"
    exit 1
}

# 调用示例：
# log_message "INFO" "This is an info message."
# log_message "ERROR" "This is an error message."
# log_message "DEBUG" "This is a debug message."

# 系统相关配置
LOG_DIR="/var/log/ubturbo"
PROGRAM_DIR="/opt/ubturbo"
PROGRAM_CONF_DIR="/opt/ubturbo/conf"
PROGRAM_LIB_DIR="/opt/ubturbo/lib"
PROGRAM_BIN_DIR="/opt/ubturbo/bin"
PROGRAM_LOG_DIR="/var/log/ubturbo"
SYSTEM_USER="ubturbo"
SYSTEM_GROUP="ubturbo"
ROOT_USER="root"
ROOT_GROUP="root"

# 创建系统组
create_group() {
    if ! getent group "$SYSTEM_GROUP" > /dev/null; then
        groupadd -r "$SYSTEM_GROUP" || handle_error "Failed to create group $SYSTEM_GROUP"
        log_message "INFO" "Group $SYSTEM_GROUP created"
    else
        log_message "INFO" "Group $SYSTEM_GROUP already exists"
    fi
}

# 创建系统用户
create_user() {
    if ! getent passwd "$SYSTEM_USER" > /dev/null; then
        useradd -r -g "$SYSTEM_GROUP" -s /sbin/nologin "$SYSTEM_USER" || handle_error "Failed to create user $SYSTEM_USER"
        log_message "INFO" "User $SYSTEM_USER created"
    else
        log_message "INFO" "User $SYSTEM_USER already exists"
    fi
}

# 创建并设置目录及其内容的属主
ensure_directory_owner() {
    local dir_path="$1"
    local recursive="${2:-false}"  # 是否递归设置内容属主，默认为 false

    # 创建目录（如果不存在）
    if [ ! -d "$dir_path" ]; then
        mkdir -p "$dir_path" || handle_error "Failed to create directory $dir_path"
        log_message "INFO" "Directory $dir_path created"
    fi

    # 获取当前目录的属主和属组
    local current_owner
    current_owner=$(stat -c "%U:%G" "$dir_path")

    # 设置目录的属主（如果不匹配）
    if [ "$current_owner" != "$SYSTEM_USER:$SYSTEM_GROUP" ]; then
        log_message "INFO" "Setting ownership for $dir_path to $SYSTEM_USER:$SYSTEM_GROUP"
        chown "$SYSTEM_USER:$SYSTEM_GROUP" "$dir_path" || handle_error "Failed to set ownership for directory $dir_path"
    fi

    # 如果递归设置内容属主
    if [ "$recursive" = true ]; then
        log_message "INFO" "Recursively setting ownership for contents of $dir_path"
        chown -R "$SYSTEM_USER:$SYSTEM_GROUP" "$dir_path" || handle_error "Failed to set ownership recursively for $dir_path"
    fi

    log_message "INFO" "Ownership for $dir_path and contents (if recursive) set to $SYSTEM_USER:$SYSTEM_GROUP"
}

# ubturbo目录与文件权限控制
ensure_permission() {
    # 目录权限控制
    chmod 750 "$PROGRAM_DIR" || handle_error "Failed to set permissions for $PROGRAM_DIR"
    chmod 700 "$PROGRAM_CONF_DIR" || handle_error "Failed to set permissions for $PROGRAM_CONF_DIR"
    chmod 500 "$PROGRAM_LIB_DIR" || handle_error "Failed to set permissions for $PROGRAM_LIB_DIR"
    chmod 500 "$PROGRAM_BIN_DIR" || handle_error "Failed to set permissions for $PROGRAM_BIN_DIR"
    chmod 700 "$PROGRAM_LOG_DIR" || handle_error "Failed to set permissions for $PROGRAM_LOG_DIR"

    # 文件权限控制
    chmod 600 "$PROGRAM_CONF_DIR"/* || handle_error "Failed to set permissions for conf files in $PROGRAM_CONF_DIR"
    chmod 600 "$PROGRAM_LOG_DIR"/* || handle_error "Failed to set permissions for log files in $PROGRAM_LOG_DIR"
    chmod 500 "$PROGRAM_BIN_DIR"/* || handle_error "Failed to set permissions for exec files in $PROGRAM_BIN_DIR"
    chmod 500 "$PROGRAM_LIB_DIR"/* || handle_error "Failed to set permissions for exec files in $PROGRAM_LIB_DIR"
}

# 拷贝服务文件
copy_service_file() {
    local src_dir="/opt/ubturbo/scripts"
    local src_file="$src_dir/ubturbo.service"
    local service_file="/etc/systemd/system/ubturbo.service"

    # 拷贝 service 文件
    cp "$src_file" "$service_file" || handle_error "Failed to copy service file"
    log_message "INFO" "Service file copied to $service_file"

    # 设置权限
    chmod 644 "$service_file" || handle_error "Failed to set permissions for $service_file"

    # 删除原 service 文件
    rm -f "$src_file" || handle_error "Failed to remove original service file"
    log_message "INFO" "Original service file removed"

    # 删除目录（如果为空）
    if [ -d "$src_dir" ]; then
        rmdir "$src_dir" 2>/dev/null && \
        log_message "INFO" "Empty directory $src_dir removed" || \
        log_message "INFO" "Directory $src_dir not empty, not removed"
    fi
}

# 拷贝libubturbo_client.so文件
copy_client_so() {
    local source_so_file="/opt/ubturbo/lib/libubturbo_client.so"
    local installed_so_file="/usr/lib64/libubturbo_client.so"

    cp "$source_so_file" "$installed_so_file" || handle_error "Failed to copy so file"
    log_message "INFO" "Smap so file copied to $installed_so_file"

    chmod 550 "$installed_so_file" || handle_error "Failed to set permissions for $installed_so_file"
    chown "$SYSTEM_USER:$SYSTEM_GROUP" "$installed_so_file" || handle_error "Failed to set ownership for directory $installed_so_file"

    # 删除源文件
    if [ -f "$source_so_file" ]; then
        rm -f "$source_so_file" || handle_error "Failed to remove source $source_so_file"
        log_message "INFO" "Removed source $source_so_file"
    fi
}

# 控制cat.sh脚本的权限
chmod_cat_sh() {
    local source_sh_file="/opt/ubturbo/bin/cat.sh"
    local installed_sh_file="/usr/local/bin/cat.sh"
 
    cp "$source_sh_file" "$installed_sh_file" || handle_error "Failed to copy so file"
    log_message "INFO" "Smap so file copied to $installed_sh_file"
 
    # 删除源文件
    if [ -f "$source_sh_file" ]; then
        rm -f "$source_sh_file" || handle_error "Failed to remove source $source_sh_file"
        log_message "INFO" "Removed source $source_sh_file"
    fi

    chmod 500 "$installed_sh_file" || handle_error "Failed to set permissions for $installed_sh_file"
    chown "$ROOT_USER:$ROOT_GROUP" "$installed_sh_file" || handle_error "Failed to set ownership for directory $installed_sh_file"
}

# 重新加载 systemd，这里只是让 systemd 重刷文件，不会影响运行的服务
reload_systemd() {
    systemctl daemon-reload || handle_error "Failed to reload systemd"
    log_message "INFO" "Systemd daemon reloaded"
}

# 主流程
main() {
    log_message "INFO" "======================"
    log_message "INFO" "post_install.sh started"
    log_message "INFO" "======================"

    create_group
    create_user
    copy_service_file
    copy_client_so
    reload_systemd
    # 确保日志和程序目录的属主正确
    ensure_directory_owner "$LOG_DIR" true
    ensure_directory_owner "$PROGRAM_DIR" true
    # 权限控制
    ensure_permission
    chmod_cat_sh

    # 将程序设为开机自启动
    systemctl enable ubturbo.service
    
    log_message "INFO" "======================"
    log_message "INFO" "post_install.sh ended"
    log_message "INFO" "======================"
}

# 执行主流程
main "$@"

%preun rmrs
#!/bin/bash

# 默认日志目录和日志文件
LOG_DIR="/var/log/ubturbo"
LOG_FILE="$LOG_DIR/ubturbo-uninstall.log"

# 检查并创建日志目录
create_log_directory() {
  # 只检查一次，减少不必要的文件系统操作
  if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR" || handle_error "Failed to create log directory $LOG_DIR"
    chmod 700 "$LOG_DIR"  # 设置日志目录权限为700
    log_message "INFO" "Log directory $LOG_DIR created successfully."
  elif [ ! -w "$LOG_DIR" ]; then
    handle_error "Log directory $LOG_DIR is not writable."
  fi
}

# 输出日志到文件和控制台
log_message() {
  local log_type="$1"
  local message="$2"

  # 获取时间戳
  local timestamp
  timestamp="$(date)"
  local log_entry="[$timestamp] [$log_type] $message"

  # 检查日志目录是否存在并且可写
  create_log_directory

  # 如果日志文件是首次创建，则设置权限为600
  if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
    chmod 600 "$LOG_FILE"  # 只在首次创建时设置权限
  fi

  # 写入日志文件
  echo "$log_entry" >> "$LOG_FILE"
}

# 统一错误处理
handle_error() {
    log_message "ERROR" "$1"
    exit 1
}

# 调用示例：
# log_message "INFO" "This is an info message."
# log_message "ERROR" "This is an error message."
# log_message "DEBUG" "This is a debug message."

# 检查服务是否存在
service_exists() {
    local service_name="$1"
    systemctl list-units --type=service --all | grep -q "$service_name"
}

# 停止并禁用服务
stop_and_disable_service() {
    local service_name="$1"

    if service_exists "$service_name"; then
        # 停止服务
        log_message "INFO" "Stopping $service_name service..."
        if ! systemctl stop "$service_name"; then
            handle_error "Failed to stop $service_name"
        fi

        # 禁用服务
        log_message "INFO" "Disabling $service_name service..."
        if ! systemctl disable "$service_name"; then
            handle_error "Failed to disable $service_name"
        fi
    else
        log_message "INFO" "$service_name does not exist, skipping stop and disable."
    fi
}

# 删除文件，如果文件不存在，则跳过
remove_file_if_exists() {
    local file="$1"

    if [ -f "$file" ]; then
        log_message "INFO" "Removing file $file..."
        if ! rm -f "$file"; then
            handle_error "Failed to remove $file"
        fi
    else
        log_message "INFO" "File $file does not exist, skipping removal."
    fi
}

# 卸载服务文件
uninstall_service() {
    # 检查服务文件是否存在并且已加载，然后重置失败状态
    if systemctl list-units --type=service | grep -q "ubturbo.service"; then
        # 如果服务已加载，重置失败状态
        systemctl reset-failed ubturbo.service || true
    fi
    local service_file="/etc/systemd/system/ubturbo.service"
    remove_file_if_exists "$service_file"
    # 重载 systemd 配置
    systemctl daemon-reload
}

# 主流程
main() {
# 检查是否是卸载操作
if [ "$1" -ne 0 ]; then
    log_message "INFO"  "Not an uninstall operation."
    chown "ubturbo:ubturbo" "/var/log/ubturbo/ubturbo-uninstall.log"
    exit 0
else
    log_message "INFO"  "Uninstalling the package pre..."
fi

log_message "$RPM_INSTALL"
log_message "INFO" "======================"
log_message "INFO" "pre_uninstall.sh started"
log_message "INFO" "======================"

# 停止并禁用服务
stop_and_disable_service "ubturbo.service"

# 卸载服务文件
uninstall_service

log_message "INFO" "======================"
log_message "INFO" "pre_uninstall.sh ended"
log_message "INFO" "======================"
}

# 执行主流程
main "$@"

%postun rmrs
#!/bin/bash

# 默认日志目录和日志文件
LOG_DIR="/var/log/ubturbo"
LOG_FILE="$LOG_DIR/ubturbo-uninstall.log"

# 检查并创建日志目录
create_log_directory() {
  # 只检查一次，减少不必要的文件系统操作
  if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR" || handle_error "Failed to create log directory $LOG_DIR"
    chmod 700 "$LOG_DIR"  # 设置日志目录权限为700
    log_message "INFO" "Log directory $LOG_DIR created successfully."
  elif [ ! -w "$LOG_DIR" ]; then
    handle_error "Log directory $LOG_DIR is not writable."
  fi
}

# 输出日志到文件和控制台
log_message() {
  local log_type="$1"
  local message="$2"

  # 获取时间戳
  local timestamp
  timestamp="$(date)"
  local log_entry="[$timestamp] [$log_type] $message"

  # 检查日志目录是否存在并且可写
  create_log_directory

  # 如果日志文件是首次创建，则设置权限为600
  if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
    chmod 600 "$LOG_FILE"  # 只在首次创建时设置权限
  fi

  # 写入日志文件
  echo "$log_entry" >> "$LOG_FILE"
}

# 统一错误处理
handle_error() {
    log_message "ERROR" "$1"
    exit 1
}

# 调用示例：
# log_message "INFO" "This is an info message."
# log_message "ERROR" "This is an error message."
# log_message "DEBUG" "This is a debug message."

# 删除指定目录（如果存在）
remove_directory_if_exists() {
    local dir="$1"
    if [ -d "$dir" ]; then
        log_message "INFO" "Removing directory $dir..."
        rm -rf "$dir" || handle_error "Failed to remove directory $dir"
    else
        log_message "INFO" "Directory $dir does not exist, skipping removal."
    fi
}

# 删除日志目录
remove_log_directory() {
    local dir="/var/log/ubturbo"
    if [ -d "$dir" ]; then
        rm -rf "$dir" || echo "Failed to remove directory $dir"
    else
        echo "Directory $dir does not exist, skipping removal."
    fi
}

# 删除用户及用户组
remove_user_and_group() {
    local user="ubturbo"
    local group="ubturbo"

    # 删除用户
    if id "$user" &>/dev/null; then
        log_message "INFO" "Removing user $user..."
        userdel -r "$user" >/dev/null 2>> "$LOG_FILE"
    else
        log_message "INFO" "User $user does not exist, skipping removal."
    fi

    # 删除用户组
    if getent group "$group" &>/dev/null; then
        log_message "INFO" "Removing group $group..."
        groupdel "$group" >/dev/null 2>> "$LOG_FILE" || handle_error "Failed to remove group $group"
    else
        log_message "INFO" "Group $group does not exist, skipping removal."
    fi
}

# 去除字符串前后空白字符的函数
trim_spaces() {
    local input="$1"
    # 使用 awk 去除首尾空格
    input=$(echo "$input" | awk '{gsub(/^[ \t]+/, ""); gsub(/[ \t]+$/, ""); print}')
    echo "$input"
}

# 主流程
main() {
# 检查是否是卸载操作
if [ "$1" -ne 0 ]; then
    log_message "INFO"  "Not an uninstall operation."
    chown "ubturbo:ubturbo" "/var/log/ubturbo/ubturbo-uninstall.log"
    exit 0
else
    log_message "INFO"  "Uninstalling the package post..."
fi
log_message "INFO" "======================"
log_message "INFO" "post_uninstall.sh started"
log_message "INFO" "======================"

# 删除用户组
remove_user_and_group

log_message "INFO" "======================"
log_message "INFO" "post_uninstall.sh ended"
log_message "INFO" "======================"
# 删除日志目录
remove_log_directory
}

# 执行主流程
main "$@"