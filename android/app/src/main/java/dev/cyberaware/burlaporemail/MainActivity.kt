package dev.cyberaware.burlaporemail

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import dev.cyberaware.burlaporemail.navigation.AppNavigation
import dev.cyberaware.burlaporemail.ui.theme.CyberAwareBaseAppTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            CyberAwareBaseAppTheme {
                Surface(color = MaterialTheme.colorScheme.background) {
                   AppNavigation()
                }
            }
        }
    }
}
        