#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
//#![cfg_attr(not(debug_assertions), windows_subsystem = "console")]

#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

use std::process::{Command, Child, Stdio};
use std::sync::Mutex;
use std::path::PathBuf;
use tauri::Manager;

struct AppState {
    django_process: Mutex<Option<Child>>,
    postgres_process: Mutex<Option<Child>>,
    data_dir: Mutex<Option<PathBuf>>,
}

fn normalize_path(path: &PathBuf) -> PathBuf {
    let path_str = path.to_string_lossy().to_string();
    if path_str.starts_with(r"\\?\") {
        PathBuf::from(path_str.trim_start_matches(r"\\?\"))
    } else {
        path.clone()
    }
}

fn get_resource_path(_app_handle: &tauri::AppHandle, resource: &str) -> Result<PathBuf, String> {
    #[cfg(debug_assertions)]
    {
        let current_exe = std::env::current_exe()
            .map_err(|e| format!("No se pudo obtener ruta del ejecutable: {}", e))?;
        
        let project_root = current_exe
            .parent()
            .and_then(|p| p.parent())
            .and_then(|p| p.parent())
            .and_then(|p| p.parent())
            .ok_or("No se pudo determinar el directorio del proyecto")?;
        
        let resource_path = project_root.join("src-tauri").join("binaries").join(resource);
        
        println!("🔍 [DEV] Buscando: {:?}", resource_path);
        
        if resource_path.exists() {
            println!("✅ [DEV] Encontrado");
            Ok(resource_path)
        } else {
            Err(format!("❌ [DEV] Recurso no encontrado: {:?}", resource_path))
        }
    }
    
    #[cfg(not(debug_assertions))]
    {
        let resource_dir = _app_handle.path()
            .resource_dir()
            .map_err(|e| format!("Error al obtener directorio de recursos: {}", e))?;
        
        println!("📁 [PROD] Resource dir: {:?}", resource_dir);
        let full_path = resource_dir.join(resource);
        
        println!("🔍 [PROD] Buscando: {:?}", full_path);
        
        if full_path.exists() {
            println!("✅ [PROD] Encontrado");
            Ok(full_path)
        } else {
            println!("❌ [PROD] No encontrado. Listando resource_dir:");
            if let Ok(entries) = std::fs::read_dir(&resource_dir) {
                for entry in entries.flatten() {
                    println!("   - {:?}", entry.path().file_name().unwrap_or_default());
                }
            }
            
            Err(format!(
                "❌ Recurso no encontrado: {:?}\n   Resource dir: {:?}\n   Los archivos no se empaquetaron correctamente.",
                full_path, resource_dir
            ))
        }
    }
}

fn check_postgres_ready() -> bool {
    use std::net::TcpStream;
    use std::time::Duration;
    
    TcpStream::connect_timeout(
        &"127.0.0.1:5433".parse().unwrap(),
        Duration::from_millis(500)
    ).is_ok()
}

fn check_django_ready() -> bool {
    use std::net::TcpStream;
    use std::time::Duration;
    
    TcpStream::connect_timeout(
        &"127.0.0.1:8000".parse().unwrap(),
        Duration::from_millis(500)
    ).is_ok()
}

fn wait_for_django_migrations(is_first_time: bool) -> bool {
    let max_wait = if is_first_time {
        println!("⏳ Primera ejecución: Esperando a que Django complete las migraciones...");
        println!("   Esto puede tomar hasta 90 segundos");
        90
    } else {
        println!("⏳ Esperando a que Django esté listo...");
        println!("   Esto debería tomar solo unos segundos");
        15
    };
    
    for attempt in 1..=max_wait {
        std::thread::sleep(std::time::Duration::from_secs(1));
        
        if check_django_ready() {
            std::thread::sleep(std::time::Duration::from_secs(2));
            
            if check_django_ready() {
                println!("✅ Django completamente listo (intento {})", attempt);
                return true;
            }
        }
        
        if is_first_time && attempt % 10 == 0 {
            println!("   ... aún esperando ({} segundos)", attempt);
        }
    }
    
    println!("⚠️ Timeout esperando a Django, pero continuando");
    false
}

fn init_postgres(app_handle: &tauri::AppHandle) -> Result<bool, String> {
    println!("🐘 Iniciando PostgreSQL...");

    let postgres_dir_raw = get_resource_path(app_handle, "postgres")?;
    let postgres_dir = normalize_path(&postgres_dir_raw);
    
    let app_data_dir = app_handle.path()
        .app_data_dir()
        .map_err(|e| format!("Error al obtener directorio de datos: {}", e))?;

    let data_dir_raw = app_data_dir.join("postgres_data");
    let data_dir = normalize_path(&data_dir_raw);

    println!("📁 Directorio de PostgreSQL: {:?}", postgres_dir);
    println!("📁 Directorio de datos: {:?}", data_dir);
    
    let bin_dir = postgres_dir.join("bin");
    if !bin_dir.exists() {
        return Err(format!("❌ Directorio bin no encontrado en: {:?}", bin_dir));
    }
    println!("✅ Directorio bin encontrado: {:?}", bin_dir);

    std::fs::create_dir_all(&data_dir)
        .map_err(|e| format!("Error al crear directorio de datos: {}", e))?;

    let initdb_exe = postgres_dir.join("bin").join("initdb.exe");
    let postgres_exe = postgres_dir.join("bin").join("postgres.exe");
    let pg_ctl_exe = postgres_dir.join("bin").join("pg_ctl.exe");

    if !initdb_exe.exists() {
        return Err(format!("❌ initdb.exe no encontrado en: {:?}", initdb_exe));
    }
    if !postgres_exe.exists() {
        return Err(format!("❌ postgres.exe no encontrado en: {:?}", postgres_exe));
    }
    if !pg_ctl_exe.exists() {
        return Err(format!("❌ pg_ctl.exe no encontrado en: {:?}", pg_ctl_exe));
    }

    println!("✅ Todos los ejecutables de PostgreSQL encontrados");

    let pid_file = data_dir.join("postmaster.pid");
    
    if pid_file.exists() {
        println!("⚠️ Limpiando sesión anterior de PostgreSQL...");
        let _ = Command::new(&pg_ctl_exe)
            .arg("stop")
            .arg("-D")
            .arg(&data_dir)
            .arg("-m")
            .arg("immediate")
            .output();
        
        std::thread::sleep(std::time::Duration::from_secs(1));
        let _ = std::fs::remove_file(&pid_file);
        println!("✅ Limpieza completada");
    }

    let pg_version_file = data_dir.join("PG_VERSION");
    let mut is_first_time = !pg_version_file.exists();

    // Si el directorio existe pero PG_VERSION no, está corrupto
    if data_dir.exists() && !pg_version_file.exists() {
        println!("⚠️ Directorio de datos corrupto, limpiando...");
        std::fs::remove_dir_all(&data_dir)
            .map_err(|e| format!("Error al limpiar directorio corrupto: {}", e))?;
        std::fs::create_dir_all(&data_dir)
            .map_err(|e| format!("Error al recrear directorio de datos: {}", e))?;
        is_first_time = true;
    }
    
    if is_first_time {
        println!("🔧 Primera ejecución: Inicializando base de datos PostgreSQL...");

        let output = Command::new(&initdb_exe)
            .arg("-D")
            .arg(&data_dir)
            .arg("-U")
            .arg("postgres")
            .arg("--encoding=UTF8")
            .arg("--locale=C")
            .arg("--auth=trust")
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .output()
            .map_err(|e| format!("Error al ejecutar initdb: {}", e))?;

        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(format!("Error al inicializar PostgreSQL: {}", error));
        }

        println!("✅ Base de datos inicializada");
    } else {
        println!("✅ Base de datos ya existe, iniciando rápidamente...");
    }

    println!("🚀 Arrancando PostgreSQL directamente con postgres.exe...");

    let lib_dir = postgres_dir.join("lib");
    let current_path = std::env::var("PATH").unwrap_or_default();
    let new_path = format!(
        "{};{};{}",
        bin_dir.display(),
        lib_dir.display(),
        current_path
    );
    
    println!("📍 PATH configurado con bin y lib de PostgreSQL");

    #[cfg(target_os = "windows")]
    const CREATE_NO_WINDOW: u32 = 0x08000000;

    let mut cmd = Command::new(&postgres_exe);
    cmd.arg("-D")
        .arg(&data_dir)
        .arg("-p")
        .arg("5433")
        .env("PATH", new_path)
        .stdout(Stdio::null())
        .stderr(Stdio::null());

    #[cfg(target_os = "windows")]
    cmd.creation_flags(CREATE_NO_WINDOW);

    let postgres_process = cmd.spawn()
        .map_err(|e| format!("Error al iniciar PostgreSQL: {}", e))?;

    println!("✅ PostgreSQL iniciado (PID: {})", postgres_process.id());

    let state = app_handle.state::<AppState>();
    *state.postgres_process.lock().unwrap() = Some(postgres_process);
    *state.data_dir.lock().unwrap() = Some(data_dir);

    println!("⏳ Esperando a que PostgreSQL esté listo...");
    
    let max_attempts = if is_first_time { 15 } else { 5 };
    
    for attempt in 1..=max_attempts {
        std::thread::sleep(std::time::Duration::from_secs(1));
        
        if check_postgres_ready() {
            println!("✅ PostgreSQL listo para aceptar conexiones (intento {})", attempt);
            println!("⏳ Esperando a que PostgreSQL termine de inicializar completamente...");
            std::thread::sleep(std::time::Duration::from_secs(3));
            return Ok(is_first_time);
        }
        
        print!(".");
        use std::io::{self, Write};
        io::stdout().flush().unwrap();
    }

    println!("\n⚠️ PostgreSQL arrancó pero puede que aún esté inicializando");
    Ok(is_first_time)
}

fn start_django(app_handle: &tauri::AppHandle, is_first_time: bool) -> Result<Child, String> {
    println!("🐍 Iniciando Django...");

    let django_exe = get_resource_path(app_handle, "django_server.exe")?;

    if !django_exe.exists() {
        return Err(format!("❌ django_server.exe no existe en: {:?}", django_exe));
    }

    println!("📍 Ejecutable Django: {:?}", django_exe);

    #[cfg(target_os = "windows")]
    const CREATE_NO_WINDOW: u32 = 0x08000000;

    let mut cmd = Command::new(&django_exe);
    cmd.env("DB_ENGINE", "django.db.backends.postgresql")
        .env("DB_NAME", "registrame_db")
        .env("DB_USER", "postgres")
        .env("DB_PASSWORD", "")
        .env("DB_HOST", "127.0.0.1")
        .env("DB_PORT", "5433")
        .stdout(Stdio::null())  // 2. Ocultar logs
        .stderr(Stdio::null());  // 2. Ocultar logs

    #[cfg(target_os = "windows")]
    cmd.creation_flags(CREATE_NO_WINDOW);

    let mut django_process = cmd.spawn()
        .map_err(|e| format!("Error al iniciar Django: {}", e))?;

    println!("✅ Django iniciado (PID: {})", django_process.id());

    std::thread::sleep(std::time::Duration::from_secs(5));
    
    match django_process.try_wait() {
        Ok(Some(status)) => {
            return Err(format!("❌ Django se cerró con código: {:?}", status));
        }
        Ok(None) => {
            println!("✅ Django proceso corriendo");
        }
        Err(e) => {
            eprintln!("⚠️ No se pudo verificar Django: {}", e);
        }
    }
    
    if !wait_for_django_migrations(is_first_time) {
        println!("⚠️ Django puede no estar completamente listo");
    }

    Ok(django_process)
}

fn cleanup_processes(app_handle: &tauri::AppHandle) {
    println!("🛑 Cerrando procesos...");
    let state = app_handle.state::<AppState>();

    // Detener Django
    if let Ok(mut guard) = state.django_process.lock() {
        if let Some(mut child) = guard.take() {
            let pid = child.id();
            let _ = child.kill();
            std::thread::sleep(std::time::Duration::from_millis(500));
            
            // Forzar cierre con taskkill si sigue corriendo
            let _ = Command::new("taskkill")
                .args(&["/PID", &pid.to_string(), "/F"])
                .output();
            
            // También matar por nombre por si acaso
            let _ = Command::new("taskkill")
                .args(&["/IM", "django_server.exe", "/F"])
                .output();
            
            println!("✅ Django detenido (PID: {})", pid);
        }
    }

    // Detener PostgreSQL
    if let Ok(mut guard) = state.postgres_process.lock() {
        if let Some(mut child) = guard.take() {
            let pid = child.id();
            let _ = child.kill();
            std::thread::sleep(std::time::Duration::from_millis(500));
            
            // Forzar cierre con taskkill si sigue corriendo
            let _ = Command::new("taskkill")
                .args(&["/PID", &pid.to_string(), "/F"])
                .output();
            
            println!("✅ PostgreSQL detenido (PID: {})", pid);
        }
    }

    // Limpieza adicional con pg_ctl
    let data_dir: Option<PathBuf> = {
        state.data_dir.lock().unwrap().clone()
    };

    if let Some(data_dir) = data_dir {
        let data_dir_normalized = normalize_path(&data_dir);
        if let Ok(postgres_dir_raw) = get_resource_path(app_handle, "postgres") {
            let postgres_dir = normalize_path(&postgres_dir_raw);
            let pg_ctl = postgres_dir.join("bin").join("pg_ctl.exe");

            let _ = Command::new(pg_ctl)
                .arg("stop")
                .arg("-D")
                .arg(&data_dir_normalized)
                .arg("-m")
                .arg("immediate")
                .output();

            println!("🛑 PostgreSQL pg_ctl ejecutado");
        }
    }
    
    println!("✅ Limpieza completada");
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    use std::fs::OpenOptions;
    use std::io::Write;

    let log_path = std::env::temp_dir().join("registrame_debug.log");
    let mut log_file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_path)
        .unwrap();

    writeln!(log_file, "\n=== INICIO ===").unwrap();
    
    println!("============================================================");
    println!("🚀 INICIANDO REGISTRAME");
    println!("============================================================");

    tauri::Builder::default()
        .manage(AppState {
            django_process: Mutex::new(None),
            postgres_process: Mutex::new(None),
            data_dir: Mutex::new(None),
        })
        .register_asynchronous_uri_scheme_protocol("asset", move |ctx, request, responder| {
            let uri = request.uri();
            let uri_str = uri.to_string();
            println!("📥 [ASSET PROTOCOL] Recibiendo petición: {}", uri_str);
            
            let path_str = uri_str
                .trim_start_matches("asset://localhost/")
                .trim_start_matches("media/");
            println!("📂 [ASSET PROTOCOL] Path extraído: {}", path_str);
            
            let base_dir = if cfg!(debug_assertions) {
                let current_exe = std::env::current_exe().unwrap();
                let project_root = current_exe
                    .parent().unwrap()
                    .parent().unwrap()
                    .parent().unwrap()
                    .parent().unwrap();
                let media_dir = project_root.join("backend").join("media");
                println!("🔧 [DEV] Base dir: {:?}", media_dir);
                media_dir
            } else {
                use tauri::Manager;
                let app_handle = ctx.app_handle();
                let app_data = app_handle.path().app_data_dir().unwrap();
                let media_dir = app_data.join("media");
                println!("📦 [PROD] Base dir: {:?}", media_dir);
                media_dir
            };
            
            let full_path = base_dir.join(path_str);
            println!("🎯 [ASSET PROTOCOL] Ruta completa: {:?}", full_path);
            
            if !full_path.exists() {
                println!("❌ [ASSET PROTOCOL] Archivo no encontrado: {:?}", full_path);
                responder.respond(
                    tauri::http::Response::builder()
                        .status(404)
                        .body(Vec::new())
                        .unwrap()
                );
                return;
            }
            
            match std::fs::read(&full_path) {
                Ok(data) => {
                    println!("✅ [ASSET PROTOCOL] Archivo leído: {} bytes", data.len());
                    
                    let mime_type = if path_str.ends_with(".png") {
                        "image/png"
                    } else if path_str.ends_with(".jpg") || path_str.ends_with(".jpeg") {
                        "image/jpeg"
                    } else if path_str.ends_with(".gif") {
                        "image/gif"
                    } else if path_str.ends_with(".webp") {
                        "image/webp"
                    } else {
                        "application/octet-stream"
                    };
                    
                    println!("📄 [ASSET PROTOCOL] MIME type: {}", mime_type);
                    
                    responder.respond(
                        tauri::http::Response::builder()
                            .status(200)
                            .header("Content-Type", mime_type)
                            .header("Access-Control-Allow-Origin", "*")
                            .body(data)
                            .unwrap()
                    );
                }
                Err(e) => {
                    println!("❌ [ASSET PROTOCOL] Error al leer archivo: {}", e);
                    responder.respond(
                        tauri::http::Response::builder()
                            .status(500)
                            .body(Vec::new())
                            .unwrap()
                    );
                }
            }
        })
        .setup(|app| {
            let app_handle = app.handle();

            println!("\n[1/2] Iniciando PostgreSQL...");
            let is_first_time = init_postgres(&app_handle)
                .map_err(|e| {
                    eprintln!("❌ Error fatal en PostgreSQL: {}", e);
                    std::process::exit(1);
                })
                .unwrap();

            println!("\n[2/2] Iniciando Django...");
            match start_django(&app_handle, is_first_time) {
                Ok(process) => {
                    let state = app_handle.state::<AppState>();
                    *state.django_process.lock().unwrap() = Some(process);
                    println!("✅ Django guardado en state");
                }
                Err(e) => {
                    eprintln!("❌ Error al iniciar Django: {}", e);
                    eprintln!("⚠️ Verifica que PostgreSQL esté corriendo");
                }
            }

            println!("\n============================================================");
            if is_first_time {
                println!("✅ Inicialización completada (Primera ejecución)");
            } else {
                println!("✅ Aplicación iniciada");
            }
            println!("============================================================\n");

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                let app_handle = window.app_handle();
                cleanup_processes(&app_handle);
            }
        })
        .run(tauri::generate_context!())
        .expect("Error al ejecutar la aplicación Tauri");
}

fn main() {
    run();
}