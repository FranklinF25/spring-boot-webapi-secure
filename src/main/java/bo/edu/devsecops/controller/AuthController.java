package bo.edu.devsecops.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private static final Logger LOGGER = LoggerFactory.getLogger(AuthController.class);

    // Credentials come from application.properties (env-var overridable), so no
    // secret is hardcoded in source code.
    @Value("${lab.auth.username}")
    private String authUsername;

    @Value("${lab.auth.password}")
    private String authPassword;

    @Value("${lab.auth.token}")
    private String authToken;

    @PostMapping("/login")
    public ResponseEntity<Map<String, String>> login(@RequestBody Map<String, String> credentials) {
        String username = credentials.getOrDefault("username", "");
        String password = credentials.getOrDefault("password", "");

        LOGGER.info("Login attempt: usuario={}", username);

        if (authUsername.equals(username) && authPassword.equals(password)) {
            return ResponseEntity.ok(Map.of(
                    "token", authToken,
                    "message", "Acceso autorizado"));
        }
        return ResponseEntity.status(401).body(Map.of("error", "Credenciales incorrectas"));
    }
}
