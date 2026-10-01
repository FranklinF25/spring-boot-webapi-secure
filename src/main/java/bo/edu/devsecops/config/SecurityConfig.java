package bo.edu.devsecops.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

import static org.springframework.security.config.Customizer.withDefaults;

@Configuration
public class SecurityConfig {

    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        // Public endpoints: the login endpoint and the comment preview used by the lab.
        // Everything else requires HTTP Basic authentication.
        return http
                .csrf(csrf -> csrf.disable())
                .httpBasic(withDefaults())
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/auth/login").permitAll()
                        .requestMatchers("/api/comments/preview").permitAll()
                        .anyRequest().authenticated())
                .build();
    }
}
