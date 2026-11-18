"""Adds the Mizan home-screen widget and the mizan://add link to the generated Android project.
Runs in the cloud build right after `npx cap add android`. Safe to run twice."""
import os, re, sys

APP = 'android/app/src/main'
PKG = 'app.mizan.budget'
JAVA = os.path.join(APP, 'java', *PKG.split('.'))
RES = os.path.join(APP, 'res')
if not os.path.isdir(APP):
    sys.exit('android project not found - run "npx cap add android" first')

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

write(os.path.join(JAVA, 'MainActivity.java'), '''package app.mizan.budget;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(MizanWidgetPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
''')

write(os.path.join(JAVA, 'MizanWidgetPlugin.java'), """package app.mizan.budget;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "MizanWidget")
public class MizanWidgetPlugin extends Plugin {
    @PluginMethod
    public void refresh(PluginCall call) {
        WidgetCommon.refreshAll(getContext());
        call.resolve();
    }
}
""")

write(os.path.join(JAVA, 'WidgetCommon.java'), """package app.mizan.budget;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import org.json.JSONObject;

final class WidgetCommon {
    private WidgetCommon() {}

    static JSONObject load(Context context) {
        try {
            String raw = context.getSharedPreferences("CapacitorStorage", Context.MODE_PRIVATE).getString("mizan_widget", null);
            if (raw != null) {
                return new JSONObject(raw);
            }
        } catch (Exception e) {
            // fall through to an empty object
        }
        return new JSONObject();
    }

    static PendingIntent open(Context context, int code) {
        Intent i = new Intent(context, MainActivity.class);
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        return PendingIntent.getActivity(context, code, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    static PendingIntent add(Context context, int code, String query) {
        Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse("mizan://add" + query), context, MainActivity.class);
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        return PendingIntent.getActivity(context, code, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    static void refreshAll(Context context) {
        AppWidgetManager m = AppWidgetManager.getInstance(context);
        int[] small = m.getAppWidgetIds(new ComponentName(context, MizanWidget.class));
        for (int id : small) {
            MizanWidget.update(context, m, id);
        }
        int[] large = m.getAppWidgetIds(new ComponentName(context, MizanWidgetLarge.class));
        for (int id : large) {
            MizanWidgetLarge.update(context, m, id);
        }
    }
}
""")

write(os.path.join(JAVA, 'MizanWidget.java'), """package app.mizan.budget;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.view.View;
import android.widget.RemoteViews;
import org.json.JSONObject;

public class MizanWidget extends AppWidgetProvider {

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        for (int id : ids) {
            update(context, manager, id);
        }
    }

    static void update(Context context, AppWidgetManager manager, int id) {
        RemoteViews v = new RemoteViews(context.getPackageName(), R.layout.mizan_widget);
        JSONObject o = WidgetCommon.load(context);
        boolean pro = o.optBoolean("pro", false);

        v.setTextViewText(R.id.w_title, o.optString("title", "Mizan"));
        v.setTextViewText(R.id.w_date, o.optString("date", ""));
        if (pro) {
            v.setTextViewText(R.id.w_pct, o.optString("pctText", ""));
            v.setTextViewText(R.id.w_cap, o.optString("cap", ""));
            v.setProgressBar(R.id.w_bar, 100, o.optInt("pct", 0), false);
            v.setViewVisibility(R.id.w_bar, View.VISIBLE);
            v.setTextViewText(R.id.w_spend, o.optString("spend", "- Spend"));
            v.setTextViewText(R.id.w_income, o.optString("income", "+ Income"));
            v.setViewVisibility(R.id.w_buttons, View.VISIBLE);
        } else {
            v.setTextViewText(R.id.w_pct, "");
            v.setTextViewText(R.id.w_cap, o.optString("locked", "Open Mizan and go Pro to use the widget"));
            v.setViewVisibility(R.id.w_bar, View.GONE);
            v.setViewVisibility(R.id.w_buttons, View.GONE);
        }

        v.setOnClickPendingIntent(R.id.w_root, WidgetCommon.open(context, 10));
        v.setOnClickPendingIntent(R.id.w_spend, WidgetCommon.add(context, 11, ""));
        v.setOnClickPendingIntent(R.id.w_income, WidgetCommon.add(context, 12, "?type=income"));
        manager.updateAppWidget(id, v);
    }
}
""")

write(os.path.join(JAVA, 'MizanWidgetLarge.java'), """package app.mizan.budget;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.graphics.Color;
import android.net.Uri;
import android.view.View;
import android.widget.RemoteViews;
import org.json.JSONArray;
import org.json.JSONObject;

public class MizanWidgetLarge extends AppWidgetProvider {

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        for (int id : ids) {
            update(context, manager, id);
        }
    }

    static void update(Context context, AppWidgetManager manager, int id) {
        RemoteViews v = new RemoteViews(context.getPackageName(), R.layout.mizan_widget_large);
        JSONObject o = WidgetCommon.load(context);
        boolean pro = o.optBoolean("pro", false);

        int[] tiles = {R.id.t1, R.id.t2, R.id.t3};
        int[] names = {R.id.t1_name, R.id.t2_name, R.id.t3_name};
        int[] amts = {R.id.t1_amt, R.id.t2_amt, R.id.t3_amt};
        int[] dots = {R.id.t1_dot, R.id.t2_dot, R.id.t3_dot};

        v.setTextViewText(R.id.w_title, o.optString("title", "Mizan"));
        v.setTextViewText(R.id.w_date, o.optString("date", ""));
        v.setOnClickPendingIntent(R.id.w_root, WidgetCommon.open(context, 20));

        if (pro) {
            v.setTextViewText(R.id.w_pct, o.optString("pctText", ""));
            v.setTextViewText(R.id.w_cap, o.optString("cap", ""));
            v.setProgressBar(R.id.w_bar, 100, o.optInt("pct", 0), false);
            v.setViewVisibility(R.id.w_bar, View.VISIBLE);
            v.setViewVisibility(R.id.w_tiles, View.VISIBLE);

            JSONArray cats = o.optJSONArray("cats");
            for (int i = 0; i < 3; i++) {
                if (cats != null && i < cats.length()) {
                    JSONObject c = cats.optJSONObject(i);
                    String catId = c == null ? "" : c.optString("id", "");
                    v.setViewVisibility(tiles[i], View.VISIBLE);
                    v.setTextViewText(names[i], c == null ? "" : c.optString("n", ""));
                    v.setTextViewText(amts[i], c == null ? "" : c.optString("a", ""));
                    int color = Color.parseColor("#1E6B5A");
                    try {
                        color = Color.parseColor(c == null ? "#1E6B5A" : c.optString("c", "#1E6B5A"));
                    } catch (Exception e) {
                        // keep the default colour
                    }
                    v.setInt(dots[i], "setBackgroundColor", color);
                    v.setOnClickPendingIntent(tiles[i], WidgetCommon.add(context, 21 + i, "?v=" + Uri.encode(catId)));
                } else {
                    v.setViewVisibility(tiles[i], View.GONE);
                }
            }
            v.setTextViewText(R.id.t4_name, o.optString("other", "Other"));
            v.setOnClickPendingIntent(R.id.t4, WidgetCommon.add(context, 25, ""));
        } else {
            v.setTextViewText(R.id.w_pct, "");
            v.setTextViewText(R.id.w_cap, o.optString("locked", "Open Mizan and go Pro to use the widget"));
            v.setViewVisibility(R.id.w_bar, View.GONE);
            v.setViewVisibility(R.id.w_tiles, View.GONE);
        }
        manager.updateAppWidget(id, v);
    }
}
""")

write(os.path.join(RES, 'values', 'mizan_colors.xml'), """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="mz_surface">#F7FBF8</color>
    <color name="mz_line">#D5DFD9</color>
    <color name="mz_ink">#14221D</color>
    <color name="mz_muted">#566860</color>
    <color name="mz_accent">#1E6B5A</color>
    <color name="mz_tile">#FFFFFF</color>
    <color name="mz_track">#E6ECE8</color>
    <color name="mz_spend_bg">#FCECE9</color>
    <color name="mz_spend_fg">#B3341F</color>
    <color name="mz_income_bg">#1E6B5A</color>
    <color name="mz_income_fg">#FFFFFF</color>
</resources>
""")
write(os.path.join(RES, 'values-night', 'mizan_colors.xml'), """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="mz_surface">#16231E</color>
    <color name="mz_line">#2B3C35</color>
    <color name="mz_ink">#E7EFEA</color>
    <color name="mz_muted">#93A59C</color>
    <color name="mz_accent">#4FB89B</color>
    <color name="mz_tile">#1B2B25</color>
    <color name="mz_track">#2B3C35</color>
    <color name="mz_spend_bg">#3A2A26</color>
    <color name="mz_spend_fg">#F28C77</color>
    <color name="mz_income_bg">#4FB89B</color>
    <color name="mz_income_fg">#0B1512</color>
</resources>
""")

def shape(name, color, radius, stroke=None):
    st = '    <stroke android:width="1dp" android:color="@color/%s" />\n' % stroke if stroke else ''
    write(os.path.join(RES, 'drawable', name + '.xml'), '<?xml version="1.0" encoding="utf-8"?>\n<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">\n    <solid android:color="@color/%s" />\n    <corners android:radius="%sdp" />\n%s</shape>\n' % (color, radius, st))
shape('mizan_widget_bg', 'mz_surface', 22, 'mz_line')
shape('mizan_tile_bg', 'mz_tile', 14, 'mz_line')
shape('mizan_btn_spend', 'mz_spend_bg', 14)
shape('mizan_btn_income', 'mz_income_bg', 14)

HEADER = """    <RelativeLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content">

        <TextView
            android:id="@+id/w_title"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:drawablePadding="6dp"
            android:text="Mizan"
            android:textColor="@color/mz_accent"
            android:textSize="14sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/w_date"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_alignParentEnd="true"
            android:textColor="@color/mz_muted"
            android:textSize="12sp" />
    </RelativeLayout>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="6dp"
        android:gravity="bottom"
        android:orientation="horizontal">

        <TextView
            android:id="@+id/w_pct"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textColor="@color/mz_ink"
            android:textSize="30sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/w_cap"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_marginStart="8dp"
            android:layout_marginBottom="5dp"
            android:layout_weight="1"
            android:maxLines="2"
            android:textColor="@color/mz_muted"
            android:textSize="12sp" />
    </LinearLayout>

    <ProgressBar
        android:id="@+id/w_bar"
        style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="match_parent"
        android:layout_height="7dp"
        android:layout_marginTop="6dp"
        android:max="100"
        android:progress="0"
        android:progressBackgroundTint="@color/mz_track"
        android:progressTint="@color/mz_accent" />
"""
write(os.path.join(RES, 'layout', 'mizan_widget.xml'), """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/w_root"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@drawable/mizan_widget_bg"
    android:orientation="vertical"
    android:padding="14dp">

""" + HEADER + """
    <LinearLayout
        android:id="@+id/w_buttons"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_marginTop="10dp"
        android:layout_weight="1"
        android:orientation="horizontal">

        <TextView
            android:id="@+id/w_spend"
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_marginEnd="6dp"
            android:layout_weight="1"
            android:background="@drawable/mizan_btn_spend"
            android:gravity="center"
            android:text="- Spend"
            android:textColor="@color/mz_spend_fg"
            android:textSize="14sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/w_income"
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_marginStart="6dp"
            android:layout_weight="1"
            android:background="@drawable/mizan_btn_income"
            android:gravity="center"
            android:text="+ Income"
            android:textColor="@color/mz_income_fg"
            android:textSize="14sp"
            android:textStyle="bold" />
    </LinearLayout>
</LinearLayout>
""")

def tile(i):
    return """        <LinearLayout
            android:id="@+id/t%d"
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_marginEnd="6dp"
            android:layout_weight="1"
            android:background="@drawable/mizan_tile_bg"
            android:gravity="center"
            android:orientation="vertical"
            android:padding="6dp">

            <View
                android:id="@+id/t%d_dot"
                android:layout_width="22dp"
                android:layout_height="4dp"
                android:layout_marginBottom="6dp" />

            <TextView
                android:id="@+id/t%d_name"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:maxLines="1"
                android:textColor="@color/mz_ink"
                android:textSize="13sp"
                android:textStyle="bold" />

            <TextView
                android:id="@+id/t%d_amt"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:maxLines="1"
                android:textColor="@color/mz_muted"
                android:textSize="12sp" />
        </LinearLayout>
""" % (i, i, i, i)
write(os.path.join(RES, 'layout', 'mizan_widget_large.xml'), """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/w_root"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@drawable/mizan_widget_bg"
    android:orientation="vertical"
    android:padding="14dp">

""" + HEADER + """
    <LinearLayout
        android:id="@+id/w_tiles"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_marginTop="10dp"
        android:layout_weight="1"
        android:orientation="horizontal">

""" + tile(1) + tile(2) + tile(3) + """
        <LinearLayout
            android:id="@+id/t4"
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_weight="1"
            android:background="@drawable/mizan_tile_bg"
            android:gravity="center"
            android:orientation="vertical"
            android:padding="6dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="+"
                android:textColor="@color/mz_accent"
                android:textSize="22sp"
                android:textStyle="bold" />

            <TextView
                android:id="@+id/t4_name"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:maxLines="1"
                android:text="Other"
                android:textColor="@color/mz_ink"
                android:textSize="13sp"
                android:textStyle="bold" />
        </LinearLayout>
    </LinearLayout>
</LinearLayout>
""")

write(os.path.join(RES, 'xml', 'mizan_widget_info.xml'), """<?xml version="1.0" encoding="utf-8"?>
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="250dp"
    android:minHeight="110dp"
    android:targetCellWidth="4"
    android:targetCellHeight="2"
    android:updatePeriodMillis="1800000"
    android:initialLayout="@layout/mizan_widget"
    android:resizeMode="horizontal|vertical"
    android:widgetCategory="home_screen" />
""")
write(os.path.join(RES, 'xml', 'mizan_widget_large_info.xml'), """<?xml version="1.0" encoding="utf-8"?>
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="250dp"
    android:minHeight="180dp"
    android:targetCellWidth="4"
    android:targetCellHeight="3"
    android:updatePeriodMillis="1800000"
    android:initialLayout="@layout/mizan_widget_large"
    android:resizeMode="horizontal|vertical"
    android:widgetCategory="home_screen" />
""")

# ---- manifest: widget receiver, mizan://add link, notification permission
mf = os.path.join(APP, 'AndroidManifest.xml')
m = open(mf, encoding='utf-8').read()
if '.MizanWidget"' not in m:
    receiver = '''
        <receiver android:name=".MizanWidget" android:exported="true">
            <intent-filter>
                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
            </intent-filter>
            <meta-data android:name="android.appwidget.provider" android:resource="@xml/mizan_widget_info" />
        </receiver>
        <receiver android:name=".MizanWidgetLarge" android:exported="true">
            <intent-filter>
                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
            </intent-filter>
            <meta-data android:name="android.appwidget.provider" android:resource="@xml/mizan_widget_large_info" />
        </receiver>
'''
    assert '</application>' in m
    m = m.replace('</application>', receiver + '    </application>', 1)
    link = '''            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="mizan" android:host="add" />
            </intent-filter>
'''
    mm = re.search(r'<activity\b[^>]*MainActivity[^>]*>.*?</activity>', m, re.S)
    assert mm, 'MainActivity block not found'
    block = mm.group(0)
    m = m.replace(block, block.replace('</activity>', link + '        </activity>'), 1)
if 'POST_NOTIFICATIONS' not in m:
    m = m.replace('</manifest>', '    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />\n</manifest>', 1)
open(mf, 'w', encoding='utf-8').write(m)
print('Mizan widget + link added')
